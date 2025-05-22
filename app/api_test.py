import pytest
from app import create_app
from http import HTTPStatus
from .weather import all_city_weather


@pytest.fixture
def client():
    """
    init test client
    """

    # Init app using factory
    app = create_app()
    with app.test_client() as client:
        yield client

    # Test is complete, clear all saved data
    all_city_weather.clear()


def test_post_weather(client):
    """
    test adding data
    """

    body = {
        "city_name": "manchester",
        "temperature": 22,
        "condition": "sunny",
        "timestamp": "2025-12-20T10:00:00Z",
    }

    response = client.post("/weather", json=body)

    assert response.json == body
    assert response.status_code == HTTPStatus.OK


def test_get_weather(client):
    """
    test adding data, then check we can retrieve it
    """

    body = {
        "city_name": "manchester",
        "temperature": 22,
        "condition": "sunny",
        "timestamp": "2025-12-20T10:00:00Z",
    }

    response = client.post("/weather", json=body)

    assert response.status_code == HTTPStatus.OK
    assert response.json == body

    # ======================================
    # get valid data
    response = client.get("/weather/manchester")

    assert response.status_code == HTTPStatus.OK
    assert response.json == body

    # ======================================
    # return 404 when city not found
    response = client.get("/weather/not_valid")

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_get_all_weather(client):
    """
    test adding multiple data, then check we can all of the data back
    """

    # Without data return empty list
    response = client.get("/weather")

    assert response.status_code == HTTPStatus.OK
    assert response.json == {"all_city_weather": []}

    # ======================================
    # Add data
    body_list = [
        {
            "city_name": "manchester",
            "temperature": 22,
            "condition": "sunny",
            "timestamp": "2025-12-20T10:00:00Z",
        },
        {
            "city_name": "london",
            "temperature": 28,
            "condition": "rainy",
            "timestamp": "2025-12-20T10:00:00Z",
        },
    ]

    for body in body_list:
        response = client.post("/weather", json=body)

        assert response.status_code == HTTPStatus.OK
        assert response.json == body

    # ======================================
    # Check we can retrieve all data

    response = client.get("/weather")

    expected_response = {"all_city_weather": body_list}

    assert response.status_code == HTTPStatus.OK
    assert response.json == expected_response


def test_delete_weather(client):
    """
    adding data, then check we can delete it
    """

    # cannot delete invalid (not yet added)
    response = client.delete("/weather/london")
    assert response.status_code == HTTPStatus.NOT_FOUND

    body = {
        "city_name": "manchester",
        "temperature": 22,
        "condition": "sunny",
        "timestamp": "2025-12-20T10:00:00Z",
    }

    response = client.post("/weather", json=body)
    assert response.status_code == 200
    assert response.json == body

    response = client.delete("/weather/manchester")
    assert response.status_code == HTTPStatus.NO_CONTENT

    # ======================================
    # manchester was deleted correctly
    response = client.get("/weather/manchester")
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_update_weather(client):
    """
    adding data, then check we can update it
    """

    body = {
        "city_name": "manchester",
        "temperature": 22,
        "condition": "sunny",
        "timestamp": "2025-12-20T10:00:00Z",
    }

    response = client.post("/weather", json=body)
    assert response.status_code == 200
    assert response.json == body

    body_updated = {
        "city_name": "manchester",
        "temperature": 28,
        "condition": "sunny",
        "timestamp": "2025-12-20T10:00:00Z",
    }

    response = client.put("/weather/manchester", json=body_updated)
    assert response.status_code == HTTPStatus.OK
    assert response.json == body_updated

    # ======================================
    # Invalid update, in the past, prior to previous weather update
    body_updated_invalid = {
        "city_name": "manchester",
        "temperature": -5,
        "condition": "sunny",
        "timestamp": "2020-01-20T10:00:00Z",
    }

    response = client.put("/weather/manchester", json=body_updated_invalid)
    assert response.status_code == HTTPStatus.BAD_REQUEST

    expected_error = {
        "code": 400,
        "description": "new weather data: 2020-01-20 10:00:00+00:00 is older than current data: 2025-12-20 10:00:00+00:00",
        "name": "Bad Request",
    }
    assert response.json == expected_error

    # ======================================
    # Cannot edit a city which has not been added yet
    body_no_city = {
        "city_name": "london",
        "temperature": 22,
        "condition": "sunny",
        "timestamp": "2025-12-20T10:00:00Z",
    }

    response = client.put("/weather/london", json=body_no_city)
    assert response.status_code == HTTPStatus.NOT_FOUND
