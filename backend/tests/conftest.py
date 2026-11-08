import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import Base,get_db
from app.models.users import User
from app.models.tasks import Task


@pytest.fixture
def db():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(autoflush=False, bind=engine)()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()
        

@pytest.fixture
def client(db):
    def override_get_db():
        yield db
    
    app.dependency_overrides[get_db] = override_get_db
    
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
    
    
@pytest.fixture
def auth_headers(client):
    password = "Test123456!"
    registration = client.post(
        "/users/",
        json={
            "username": "taskuser",
            "email": "task@example.com",
            "password": password,
            "first_name": "Task",
            "last_name": "User",
        },
    )
    
    assert registration.status_code == 201, registration.text
    login_response = client.post(
        "/users/login",
        data={
            "username": "taskuser",
            "password": password
        },
    )
    
    assert login_response.status_code == 200, login_response.text
    token = login_response.json()["access_token"]
    return {
        "Authorization": f"Bearer {token}"
    }
    

@pytest.fixture
def task(client, auth_headers):
    create_response = client.post(
        "/tasks/create",
        json={
            "title": "test title",
            "description": "test description"
        },
        headers=auth_headers,
    )
    
    assert create_response.status_code == 200
    return create_response.json()


@pytest.fixture
def tasks(client, auth_headers):
    
    tasks_data = [
        {
            "title": "Task 1",
            "description": "First task",
        },
        {
            "title": "Task 2",
            "description": "Second task",
        },
        {
            "title": "Task 3",
            "description": "Third task",
        },
        {
            "title": "Task 4",
            "description": "Fourth task",
        },
    ]
    
    created_tasks = []
    
    for task_data in tasks_data:
        response = client.post(
            "/tasks/create",
            json=task_data,
            headers=auth_headers,
        )
        assert response.status_code == 200
        created_tasks.append(response.json())
    
    for task in created_tasks[:2]:
        response = client.patch(
            f"/tasks/{task['id']}",
            json={
                "completed": True,
            },
            headers=auth_headers,
        )

        assert response.status_code == 200

    return created_tasks
