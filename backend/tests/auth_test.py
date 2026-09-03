def test_register_user(client):
    response = client.post(
        "/users/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "Test123456!",
            "first_name": "Test",
            "last_name": "User",
        },
    )

    assert response.status_code == 201