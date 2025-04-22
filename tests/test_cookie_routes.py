import json


def test_get_all_cookies(client):

    response = client.get('/cookies/')
    assert response.status_code == 200

    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 2  # since we added two mock cookies

    assert "name" in data[0]
    assert "description" in data[0]
    assert "price" in data[0]
    assert "inventory_count" in data[0]

    assert "name" in data[1]
    assert "description" in data[1]
    assert "price" in data[1]
    assert "inventory_count" in data[1]



def test_get_cookie_by_id(client):

    # assuming ID 1 exists (from mock data)
    good_id = 0
    response = client.get(f'/cookies/{good_id}')
    assert response.status_code == 200

    data = response.get_json()
    assert data["id"] == good_id
    assert data["name"] == "Chocolate Chip"
    assert data["description"] == "A regular chocolate chip cookie"
    assert data["price"] == 2.99
    assert data["inventory_count"] == 100



def test_get_cookie_by_bad_id(client):

    bad_id = 1000
    response = client.get(f'/cookies/{bad_id}')
    assert response.status_code == 404

    data = response.get_json()
    assert data["message"] == f'Cookie with ID {bad_id} not found'



def test_get_cookie_with_non_integer_id(client):
    response = client.get('/cookies/bad_input')
    assert response.status_code == 404

    # Flask won't not even hit handler if input is not an int
    assert b'Not Found' in response.data




def test_patch_cookie(client):
    patch_data = {
        "price": 3.99,
        "inventory_count": 42
    }
    id = 0
    response = client.patch(f'/cookies/{id}', json=patch_data)
    assert response.status_code == 200
    data = response.get_json()

    # Makes sure these vars aren't changed
    assert data["id"] == id
    assert data["name"] == "Chocolate Chip"
    assert data["description"] == "A regular chocolate chip cookie"

    # Make sure the patched vars DO change
    assert data["price"] == 3.99
    assert data["inventory_count"] == 42




def test_post_cookie(client):
    
    new_cookie = {
        "name": "Peanut Butter Cookie",
        "description": "Cookie with made with peanut butter batter",
        "price": 1.99,
        "inventory_count": 50
    }
    response = client.post('/cookies/', json=new_cookie)
    assert response.status_code == 201
    data = response.get_json()

    assert data["id"] == 2 # Make sure ID is updated properly 

    # Check that vars are as desired
    assert data["name"] == new_cookie["name"]
    assert data["description"] == new_cookie["description"]
    assert data["price"] == new_cookie["price"]
    assert data["inventory_count"] == new_cookie["inventory_count"]



def test_get_cookie_by_id_after_post(client):

    new_id = 2
    response = client.get(f'/cookies/{new_id}')
    assert response.status_code == 200

    data = response.get_json()
    assert data["id"] == new_id
    assert data["name"] == "Peanut Butter Cookie"
    assert data["description"] == "Cookie with made with peanut butter batter"
    assert data["price"] == 1.99
    assert data["inventory_count"] == 50




def test_delete_cookie(client):

    delete_id = 2
    # Then, delete it
    delete_resp = client.delete(f'/cookies/{delete_id}')
    assert delete_resp.status_code == 204

    # Finally, verify it's gone
    get_resp = client.get(f'/cookies/{delete_id}')
    assert get_resp.status_code == 404




# TODO: add GET /cookie price-filter test(s)



# TODO: add GET /cookie name-filter test(s)