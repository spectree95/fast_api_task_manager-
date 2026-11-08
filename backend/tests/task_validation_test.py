import pytest

from app.models.tasks import Task


@pytest.mark.parametrize("payload", [
    {},
    {"title": ""},
    {"title": " \t\n "},
    {"title": None},
    {"title": 123},
    {"title": "x" * 256},
    {"title": "Task", "description": "x" * 1001},
    {"title": "Task", "description": None},
    {"title": "Task", "owner_id": 999},
])
def test_invalid_create_does_not_store_task(client, auth_headers, payload):
    response = client.post("/tasks/create", headers=auth_headers, json={"description": "", **payload})

    assert response.status_code == 422, response.text
    assert client.get("/tasks", headers=auth_headers).json()["total"] == 0


def test_create_trims_title_and_defaults_description(client, auth_headers):
    response = client.post(
        "/tasks/create", headers=auth_headers, json={"title": "  Новый проект \n"},
    )

    assert response.status_code == 200, response.text
    assert response.json()["title"] == "Новый проект"
    assert response.json()["description"] == ""


def test_create_accepts_field_length_boundaries(client, auth_headers):
    payload = {"title": "я" * 255, "description": "я" * 1000}
    response = client.post("/tasks/create", headers=auth_headers, json=payload)

    assert response.status_code == 200, response.text
    assert response.json()["title"] == payload["title"]
    assert response.json()["description"] == payload["description"]


@pytest.mark.parametrize("payload", [
    {"title": ""},
    {"title": " \t\n "},
    {"title": None},
    {"title": "x" * 256},
    {"description": None},
    {"description": "x" * 1001},
    {"completed": None},
    {"completed": "false"},
    {"completed": 1},
    {"owner_id": 999},
    {"title": "Changed", "description": "x" * 1001},
])
def test_invalid_update_leaves_task_unchanged(client, auth_headers, task, payload):
    url = f"/tasks/{task['id']}"
    response = client.patch(url, headers=auth_headers, json=payload)

    assert response.status_code == 422, response.text
    assert client.get(url, headers=auth_headers).json() == task


def test_partial_update_preserves_other_fields_and_allows_clearing_description(client, auth_headers, task):
    url = f"/tasks/{task['id']}"
    response = client.patch(url, headers=auth_headers, json={"title": "  Новое имя  "})

    assert response.status_code == 200, response.text
    assert response.json()["title"] == "Новое имя"
    assert response.json()["description"] == task["description"]
    assert response.json()["completed"] is False

    response = client.patch(url, headers=auth_headers, json={"description": "", "completed": True})
    assert response.status_code == 200, response.text
    assert response.json()["description"] == ""
    assert response.json()["completed"] is True

    response = client.patch(url, headers=auth_headers, json={})
    assert response.status_code == 200, response.text
    assert response.json()["title"] == "Новое имя"
    assert response.json()["completed"] is True


def test_existing_task_with_null_description_remains_readable(client, auth_headers, task, db):
    saved = db.get(Task, task["id"])
    saved.description = None
    db.commit()

    response = client.get(f"/tasks/{task['id']}", headers=auth_headers)
    assert response.status_code == 200, response.text
    assert response.json()["description"] is None
    response = client.get("/tasks", headers=auth_headers)
    assert response.status_code == 200, response.text
    assert response.json()["items"][0]["description"] is None
