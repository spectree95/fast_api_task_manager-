
def test_create_task(client, auth_headers):

    response = client.post(
        "/tasks/create",
        json={
            "title": "Learn pytest",
            "description": "Write integration tests",
        },
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["title"] == "Learn pytest"
    assert data["description"] == "Write integration tests"
    assert data["completed"] is False
    
    
    
def test_get_tasks(client, auth_headers, task):
   
    response = client.get(
        "/tasks",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, dict)
    assert "items" in data
    assert "total" in data
    assert "skip" in data
    assert "limit" in data

    assert isinstance(data["items"], list)
    assert len(data["items"]) >= 1
    assert data["items"][0]["title"] == "test title"
    


def test_update_task(client, auth_headers, task):
    
    task_id = task["id"]
    
    update_response = client.patch(
        f"tasks/{task_id}",
        json={
            "description": "test"
        },
        headers=auth_headers,
    )
    
    assert update_response.status_code == 200 
    
    updated_task = update_response.json()
    
    assert updated_task["id"] == task_id
    assert updated_task["description"] == "test"
    
    
def test_delete_task(client, auth_headers, task):
    
    task_id = task["id"]
    
    
    delete_task = client.delete(
        f"/tasks/{task_id}",
        headers=auth_headers,
    )
    
    assert delete_task.status_code == 204
    
    get_task = client.get(
        f"tasks/{task_id}",
        headers=auth_headers,
    )
    
    assert get_task.status_code == 404
    
def test_stranger_task_(client, auth_headers, task):
    
    task_id = task["id"]
    
    client.post(
        "/users/logout",
    )

    
    password2 = "Test123456!"
    client.post(
        "users/register",
        json={
            "username": "taskuser2",
            "email": "task2@example.com",
            "password": password2,
            "first_name": "Task2",
            "last_name": "User2",
        },
    )
    
    login_response2 = client.post(
        "/users/login",
        data={
            "username": "taskuser2",
            "password": password2,
        },
    )
    
    assert login_response2.status_code == 200 
    
    token2 = login_response2.json()["access_token"]
    headers2 = {"Authorization": f"Bearer {token2}"}
    
    get_stranger_task = client.get(
        f"/tasks/{task_id}",
        headers=headers2,
    )
    
    assert get_stranger_task.status_code == 404
    
    update_stranger_task = client.patch(
        f"/tasks/{task_id}",
        json={
            "description": "task descrpt 2"
        },
        headers=headers2,
    )
    
    get_task = client.get(
        f"/tasks/{task_id}",
        headers=auth_headers,
    )
    
    task_values = get_task.json()
    
    assert update_stranger_task.status_code == 404
    assert task_values["description"] == "test description"
    
    delete_stranger_response = client.delete(
        f"/tasks/{task_id}",
        headers=headers2,
    )
    
    assert delete_stranger_response.status_code == 404
    
    assert get_task.status_code == 200     
    
    
    
    

def test_without_jwt(client):
    
    
    create_response = client.post(
        "/tasks/create",
        json={
            "title": "title",
            "description": "descrp"
        },
    )
    
    assert create_response.status_code == 401