import pytest
from scraper.parser import parse_product_with_driver
from app.models import Product


@pytest.fixture
def product_url_full():
    return "https://www.mcdonalds.com/ua/uk-ua/product/200428.html"  # Тейсті Джуніор


@pytest.fixture
def product_url_minimal():
    return "https://www.mcdonalds.com/ua/uk-ua/product/7317.html"  # ВОДА НЕГАЗОВАНА велика


def test_parse_full_product(product_url_full):
    """Product with all data available"""
    product: Product = parse_product_with_driver(product_url_full)

    assert product.name is not None
    assert product.description is not None
    assert isinstance(product.calories, float)
    assert isinstance(product.fats, float)
    assert isinstance(product.carbs, float)
    assert isinstance(product.proteins, float)
    assert isinstance(product.unsaturated_fats, float)
    assert isinstance(product.sugar, float)
    assert isinstance(product.salt, float)
    assert isinstance(product.portion, float)


def test_parse_minimal_product(product_url_minimal):
    """Product with almost all fields as N/A except portion and name"""
    product: Product = parse_product_with_driver(product_url_minimal)

    assert product.name is not None
    assert isinstance(product.name, str)

    # Optional description may be missing
    assert product.description is None or isinstance(product.description, str)

    # All nutrients should be None
    assert product.calories is None
    assert product.fats is None
    assert product.carbs is None
    assert product.proteins is None
    assert product.unsaturated_fats is None
    assert product.sugar is None
    assert product.salt is None

    # Portion is expected to be parsed
    assert isinstance(product.portion, float)
