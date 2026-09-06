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

    # 1. API успешно создал пользователя
    assert response.status_code == 201

    # 2. Проверяем, что пользователь реально появился в БД
    user = db.execute(
        select(User).where(User.username == "testuser")
    ).scalar_one_or_none()

    assert user is not None

    # 3. Проверяем основные данные
    assert user.email == "test@example.com"
    assert user.first_name == "Test"
    assert user.last_name == "User"

    # 4. Пароль НЕ должен храниться в открытом виде
    assert user.password != password

    # 5. У нас Argon2
    assert user.password.startswith("$argon2")
    
    
def test_login_user(client):
    password = "Test123456!"

    # Сначала создаём пользователя
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

    # Теперь логинимся
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

    # 1. Регистрируем пользователя
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

    # 2. Логинимся
    login_response = client.post(
        "/users/login",
        data={
            "username": "meuser",
            "password": password,
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    # 3. Отправляем JWT в Authorization header
    response = client.get(
        "/users/me",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    # 4. Проверяем ответ
    assert response.status_code == 200

    data = response.json()

    assert data["username"] == "meuser"
    assert data["email"] == "me@example.com"
    assert data["first_name"] == "Me"
    assert data["last_name"] == "User"