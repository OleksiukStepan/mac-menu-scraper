from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Example product names from the actual JSON
full_product = "Картопля Фрі велика"
minimal_product = "ВОДА ГАЗОВАНА велика"


def test_get_all_products():
    response = client.get("/all_products/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "name" in data[0]


def test_get_existing_product():
    response = client.get(f"/products/{full_product}")
    assert response.status_code == 200
    product = response.json()
    assert product["name"] == full_product
    assert "calories" in product


def test_get_nonexistent_product():
    response = client.get("/products/Неіснуючий продукт")
    assert response.status_code == 404


def test_get_field_of_existing_product():
    response = client.get(f"/products/{full_product}/calories")
    assert response.status_code == 200
    value = response.json()["calories"]
    assert isinstance(value, (int, float, type(None)))


def test_get_field_of_minimal_product():
    response = client.get(f"/products/{minimal_product}/portion")
    assert response.status_code == 200
    value = response.json()["portion"]
    assert isinstance(value, (int, float, type(None)))


def test_invalid_field_name():
    response = client.get(f"/products/{full_product}/invalidfield")
    assert response.status_code == 422
