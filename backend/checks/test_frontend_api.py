"""Isolated API contract checks. Never reads or modifies the configured database.

Run from backend: venv/Scripts/python.exe -m unittest discover -s checks -v
"""
import fnmatch
import os
import unittest
from unittest.mock import patch

os.environ.update({
    "DATABASE_URL": "sqlite://",
    "TEST_DATABASE_URL": "sqlite://",
    "REDIS_URL": "",
    "CACHE_TTL_SECONDS": "60",
    "CACHE_TASKS_KEY": "frontend-checks",
    "SECRET_KEY": "isolated-tests-only-key-not-used-outside-this-process",
    "ALGORITHM": "HS256",
    "ACCESS_TOKEN_EXPIRE_MINUTES": "30",
})

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from redis import ConnectionError

from app.main import app
from app.core.database import Base, get_db
from app.cache.cache import RedisCacheBackend


class MemoryRedis:
    def __init__(self):
        self.values = {}

    def get(self, name):
        return self.values.get(name)

    def set(self, name, value, ex=None):
        self.values[name] = value

    def delete(self, name):
        self.values.pop(name, None)

    def scan_iter(self, match, count=100):
        return iter([key for key in self.values if fnmatch.fnmatch(key, match)])


class FrontendApiTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)()

        def override_db():
            yield self.session

        app.dependency_overrides[get_db] = override_db
        self.memory = MemoryRedis()
        cache = RedisCacheBackend("")
        cache.redis = self.memory
        self.cache_patch = patch("app.services.tasks.RedisCacheBackend", return_value=cache)
        self.cache_patch.start()
        self.client = TestClient(app)

    def tearDown(self):
        self.client.close()
        self.cache_patch.stop()
        app.dependency_overrides.clear()
        self.session.close()
        self.engine.dispose()

    def account(self, name="alex"):
        response = self.client.post("/users/", json={
            "username": name, "email": f"{name}@example.com", "password": "TestPassword123!",
            "first_name": "Александр", "last_name": "Тестовый",
        })
        self.assertEqual(response.status_code, 201, response.text)
        response = self.client.post("/users/login", data={"username": name, "password": "TestPassword123!"})
        self.assertEqual(response.status_code, 200, response.text)
        return {"Authorization": f"Bearer {response.json()['access_token']}"}

    def create_task(self, headers, title="Новая задача"):
        response = self.client.post("/tasks/create", headers=headers, json={"title": title, "description": "Описание"})
        self.assertEqual(response.status_code, 200, response.text)
        return response.json()

    def test_registration_login_and_profile(self):
        headers = self.account()
        response = self.client.get("/users/me", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["first_name"], "Александр")
        self.assertNotIn("password", response.json())
        response = self.client.patch("/users/", headers=headers, json={"first_name": "Новое имя", "username": "alex"})
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["first_name"], "Новое имя")
        self.assertEqual(self.client.post("/users/login", data={"username": "missing", "password": "wrong"}).status_code, 401)
        self.assertEqual(self.client.post("/users/login", data={"username": "alex", "password": "wrong"}).status_code, 401)
        self.assertEqual(self.client.get("/tasks").status_code, 401)

    def test_task_crud_and_cache_invalidation(self):
        headers = self.account()
        self.assertEqual(self.client.get("/tasks", headers=headers).json()["total"], 0)
        task = self.create_task(headers)
        task_url = f"/tasks/{task['id']}"
        self.assertEqual(self.client.get("/tasks", headers=headers).json()["total"], 1)
        self.assertFalse(self.client.get(task_url, headers=headers).json()["completed"])
        response = self.client.patch(task_url, headers=headers, json={"title": "Готовая задача", "completed": True})
        self.assertEqual(response.status_code, 200, response.text)
        self.assertTrue(self.client.get(task_url, headers=headers).json()["completed"])
        self.assertEqual(self.client.get("/tasks", headers=headers).json()["items"][0]["title"], "Готовая задача")
        self.assertEqual(self.client.delete(task_url, headers=headers).status_code, 204)
        self.assertEqual(self.client.get(task_url, headers=headers).status_code, 404)
        self.assertEqual(self.client.get("/tasks", headers=headers).json()["total"], 0)

    def test_ownership_filters_sorting_pagination_and_cache_keys(self):
        first, second = self.account("first"), self.account("second")
        a = self.create_task(first, "Альфа")
        self.create_task(first, "Бета")
        other = self.create_task(second, "Чужая задача")
        self.client.patch(f"/tasks/{a['id']}", headers=first, json={"completed": True})
        self.assertEqual(self.client.get("/tasks", headers=first).json()["total"], 2)
        self.assertEqual(self.client.get("/tasks", headers=second).json()["total"], 1)
        completed = self.client.get("/tasks?completed=true", headers=first).json()
        active = self.client.get("/tasks?completed=false", headers=first).json()
        self.assertEqual(completed["total"], 1)
        self.assertEqual(active["total"], 1)
        self.assertTrue(completed["items"][0]["completed"])
        self.assertFalse(active["items"][0]["completed"])
        page = self.client.get("/tasks?sort=title&order=asc&skip=1&limit=1", headers=first).json()
        self.assertEqual(page["total"], 2)
        self.assertEqual(page["items"][0]["title"], "Бета")
        self.assertEqual(self.client.get("/tasks?limit=101", headers=first).status_code, 422)
        other_url = f"/tasks/{other['id']}"
        self.client.get(other_url, headers=second)  # Prime the other user's cache.
        self.assertEqual(self.client.get(other_url, headers=first).status_code, 404)
        self.assertEqual(self.client.patch(other_url, headers=first, json={"completed": True}).status_code, 404)
        self.assertEqual(self.client.delete(other_url, headers=first).status_code, 404)

    def test_cache_outage_falls_back_to_database(self):
        headers = self.account()
        self.create_task(headers)
        with patch.object(self.memory, "get", side_effect=ConnectionError), patch.object(self.memory, "set", side_effect=ConnectionError):
            response = self.client.get("/tasks", headers=headers)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["total"], 1)
        with patch.object(self.memory, "scan_iter", side_effect=ConnectionError):
            self.create_task(headers, "Работа без кэша")

    def test_search_cache_is_scoped_and_invalidated(self):
        first, second = self.account("first"), self.account("second")
        task = self.create_task(first, "Release API")
        other = self.create_task(second, "Private API")

        def search(headers, query="API"):
            response = self.client.get("/tasks", headers=headers, params={"q": query})
            self.assertEqual(response.status_code, 200, response.text)
            return response.json()

        self.assertEqual(search(first)["items"][0]["id"], task["id"])
        self.assertEqual(search(second)["items"][0]["id"], other["id"])
        self.assertEqual(search(first, "absent")["total"], 0)
        self.assertEqual(search(first)["total"], 1)

        # A repeated query must use the correctly scoped cached result.
        with patch("app.repositories.task.TaskRepository.get_tasks", side_effect=AssertionError("Cache miss")):
            self.assertEqual(search(first)["items"][0]["id"], task["id"])
            self.assertEqual(search(second)["items"][0]["id"], other["id"])
            self.assertEqual(search(first, "absent")["total"], 0)

        created = self.create_task(first, "Document API")
        self.assertEqual(search(first)["total"], 2)
        response = self.client.patch(f"/tasks/{task['id']}", headers=first, json={"title": "Renamed"})
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(search(first)["total"], 1)
        self.assertEqual(self.client.delete(f"/tasks/{created['id']}", headers=first).status_code, 204)
        self.assertEqual(search(first)["total"], 0)
        self.assertEqual(search(second)["total"], 1)


if __name__ == "__main__":
    unittest.main()
