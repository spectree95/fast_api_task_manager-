import pytest


@pytest.fixture
def searchable_tasks(client, auth_headers):
    rows = [
        ("Release API", "Prepare the server", False),
        ("Write documentation", "Explain the API endpoints", True),
        ("Plan API tests", "Check filters and pagination", False),
        ("Buy groceries", "Milk and bread", False),
        ("План на неделю", "Обсудить проект", False),
        ("100% ready", "Literal percent", False),
        ("task_name", "Literal underscore", False),
        ("docs/api", "Literal escape character", False),
    ]
    result = []
    for title, description, completed in rows:
        response = client.post(
            "/tasks/create", headers=auth_headers,
            json={"title": title, "description": description},
        )
        assert response.status_code == 200, response.text
        task = response.json()
        if completed:
            response = client.patch(
                f"/tasks/{task['id']}", headers=auth_headers, json={"completed": True},
            )
            assert response.status_code == 200, response.text
            task = response.json()
        result.append(task)
    return result


@pytest.mark.parametrize("query, expected", [
    ("  aPi  ", {"Release API", "Write documentation", "Plan API tests", "docs/api"}),
    ("проект", {"План на неделю"}),
    ("%", {"100% ready"}),
    ("_", {"task_name"}),
    ("/", {"docs/api"}),
    ("' OR 1=1 --", set()),
    ("missing task", set()),
])
def test_search_matches_title_or_description_as_literal_text(client, auth_headers, searchable_tasks, query, expected):
    response = client.get("/tasks", headers=auth_headers, params={"q": query})

    assert response.status_code == 200, response.text
    assert {task["title"] for task in response.json()["items"]} == expected
    assert response.json()["total"] == len(expected)


def test_search_composes_with_status_sorting_and_pagination(client, auth_headers, searchable_tasks):
    params = {"q": "API", "completed": "false", "sort": "title", "order": "asc", "limit": 1, "skip": 1}
    response = client.get("/tasks", headers=auth_headers, params=params)

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["total"] == 3
    assert data["skip"] == 1
    assert data["limit"] == 1
    assert [task["title"] for task in data["items"]] == ["Release API"]

    params.update(skip=10)
    data = client.get("/tasks", headers=auth_headers, params=params).json()
    assert data["items"] == []
    assert data["total"] == 3

    params.update(skip=0, completed="true")
    data = client.get("/tasks", headers=auth_headers, params=params).json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "Write documentation"


@pytest.mark.parametrize("query", ["", "  \t  "])
def test_empty_search_returns_all_tasks(client, auth_headers, searchable_tasks, query):
    response = client.get("/tasks", headers=auth_headers, params={"q": query})
    assert response.status_code == 200, response.text
    assert response.json()["total"] == len(searchable_tasks)


@pytest.mark.parametrize("params", [
    {"q": "x" * 256}, {"skip": -1}, {"limit": 0}, {"limit": 101},
    {"sort": "owner_id"}, {"order": "invalid"}, {"completed": "invalid"},
])
def test_invalid_filters_return_validation_error(client, auth_headers, params):
    response = client.get("/tasks", headers=auth_headers, params=params)
    assert response.status_code == 422, response.text
