import pytest


def test_filter_completed(client, auth_headers, tasks):
    
    true_response = client.get(
        "/tasks?completed=True",
        headers=auth_headers,
    )
    
    assert true_response.status_code == 200
    
    data = true_response.json()
    assert len(data["items"]) == 2
    for task in data["items"]:
        assert task["completed"] == True
     
    false_response = client.get(
        "/tasks?completed=false",
        headers=auth_headers,
    )
    assert false_response.status_code == 200
    
    f_data = false_response.json()
    assert len(f_data["items"]) == 2 
    for task in f_data["items"]:
        assert task["completed"] == False
    
    
    
@pytest.mark.parametrize(
    "order, reverse",
    [
        ("asc", False,),
        ("desc", True,)
    ]
)    
def test_sort_order(client, auth_headers, tasks, order,reverse):
    
    response = client.get(
        f"/tasks?sort=title&order={order}",
        headers=auth_headers,
    )
    
    assert response.status_code == 200
    
    data = response.json()
    titles = [
        task["title"]
        for task in data["items"]
    ]
    
    assert titles == sorted(titles, reverse=reverse)
    
    
    
@pytest.mark.parametrize(
    "order,reverse",
    [
        ("asc", False,),
        ("desc", True)
    ]
)    
def test_all_filters(client, auth_headers, tasks, order, reverse):
    
    response = client.get(
        f"/tasks?sort=title&order={order}&skip=1&limit=3",
        headers=auth_headers,
    )
    assert response.status_code == 200
    
    data = response.json()
    titles = [
        task["title"]
        for task in data["items"]
    ]
    assert titles == sorted(titles, reverse=reverse)
    assert len(titles) == 3 