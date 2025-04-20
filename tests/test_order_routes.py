import json
from datetime import datetime, timedelta


def test_get_all_orders(client):

    response = client.get('/orders/')
    assert response.status_code == 200

    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 1  # since we added one mock order to start

    assert "cookies_and_quantities" in data[0]
    assert "order_date" in data[0]
    assert "deliver_date" in data[0]
    assert "status" in data[0]


    assert data[0]["cookies_and_quantities"] == {"1": 5, "0": 2}
    assert data[0]["order_date"] == '2025-01-20T15:30:00Z'.replace('Z', '+00:00')
    assert data[0]["deliver_date"] == '2025-02-02T15:30:00Z'.replace('Z', '+00:00')
    assert data[0]["status"] == "PENDING"




def test_get_order_by_id(client):

    good_id = 0

    response = client.get(f'/orders/{good_id}')
    assert response.status_code == 200

    data = response.get_json()


    assert "id" in data
    assert data["id"] ==  good_id

    assert data["cookies_and_quantities"] == {"1": 5, "0": 2}
    assert data["order_date"] == '2025-01-20T15:30:00Z'.replace('Z', '+00:00')
    assert data["deliver_date"] == '2025-02-02T15:30:00Z'.replace('Z', '+00:00')
    assert data["status"] == "PENDING"



def test_get_order_by_bad_id(client):

    bad_id = 1000
    response = client.get(f'/orders/{bad_id}')
    assert response.status_code == 404

    data = response.get_json()
    assert data["message"] == f'Order with ID {bad_id} not found'



def test_get_order_with_non_integer_id(client):
    response = client.get('/orders/bad_input')
    assert response.status_code == 404

    # Flask won't not even hit handler if input is not an int
    assert b'Not Found' in response.data





def test_patch_order_valid_transition(client):
    patch_data = {
        "status": "COOKING",
    }
    id = 0
    response = client.patch(f'/orders/{id}', json=patch_data)
    assert response.status_code == 200
    data = response.get_json()

    # Makes sure these vars aren't changed
    assert data["cookies_and_quantities"] == {"1": 5, "0": 2}
    assert data["order_date"] == '2025-01-20T15:30:00Z'.replace('Z', '+00:00')
    assert data["deliver_date"] == '2025-02-02T15:30:00Z'.replace('Z', '+00:00')

    # Make sure the status changes
    assert data["status"] == "COOKING"


    # Make sure status stays as COOKING
    response = client.get(f'/orders/{id}')
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] != "PENDING"
    assert data["status"] == "COOKING"



def test_patch_order_valid_transition(client):
    patch_data = {
        "status": "DELIVERED",
    }
    id = 0
    response = client.patch(f'/orders/{id}', json=patch_data)

    assert response.status_code == 400


# TODO: test create an order

# TODO: test delete by id

# TODO: test order filtering

# TODO: test status transition validation

# TODO: etc