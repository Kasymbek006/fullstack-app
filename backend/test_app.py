import pytest
from app import app

# -------------------------
# TEST CLIENT
# -------------------------
@pytest.fixture
def client():
    app.testing = True
    return app.test_client()


# -------------------------
# GET TEST
# -------------------------
def test_get_data(client):
    response = client.get("/api/data")

    assert response.status_code == 200
    assert isinstance(response.json, list)


# -------------------------
# POST TEST
# -------------------------
def test_add_data(client):
    response = client.post(
        "/api/data",
        json={"name": "test_item"}
    )

    assert response.status_code == 201
    assert "id" in response.json
