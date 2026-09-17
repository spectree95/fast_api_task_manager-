from sqlalchemy import select

from app.models.users import User


def test_register_user(client, db):
    password = "Test123456!"

    response = client.post(
        "/users/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": password,
            "first_name": "Test",
            "last_name": "User",
        },
    )

    assert response.status_code == 201

    user = db.execute(
        select(User).where(User.username == "testuser")
    ).scalar_one_or_none()

    assert user is not None

    assert user.email == "test@example.com"
    assert user.first_name == "Test"
    assert user.last_name == "User"

    assert user.password != password

    assert user.password.startswith("$argon2")
    
    
def test_login_user(client):
    password = "Test123456!"

    register_response = client.post(
        "/users/register",
        json={
            "username": "loginuser",
            "email": "login@example.com",
            "password": password,
            "first_name": "Login",
            "last_name": "User",
        },
    )

    assert register_response.status_code == 201

    response = client.post(
        "/users/login",
        data={
            "username": "loginuser",
            "password": password,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"
    
    
def test_get_current_user(client):
    password = "Test123456!"

    register_response = client.post(
        "/users/register",
        json={
            "username": "meuser",
            "email": "me@example.com",
            "password": password,
            "first_name": "Me",
            "last_name": "User",
        },
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/users/login",
        data={
            "username": "meuser",
            "password": password,
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.get(
        "/users/me",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["username"] == "meuser"
    assert data["email"] == "me@example.com"
    assert data["first_name"] == "Me"
    assert data["last_name"] == "User"