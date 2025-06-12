import json

from fastapi import APIRouter, HTTPException

from app.enums import ProductField
from config import JSON_OUTPUT_PATH

router = APIRouter()


# Load products from JSON
def load_products():
    try:
        with open(JSON_OUTPUT_PATH, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Products data not found")


@router.get("/all_products/")
def get_all_products():
    """Return all products"""
    return load_products()


@router.get("/products/{product_name}")
def get_product_by_name(product_name: str):
    """Return one product by name"""
    products = load_products()
    for product in products:
        if product["name"].lower() == product_name.lower():
            return product
    raise HTTPException(status_code=404, detail="Product not found")


@router.get("/products/{product_name}/{product_field}")
def get_product_field(product_name: str, product_field: ProductField):
    """Return a specific field from a product"""
    products = load_products()
    for product in products:
        if product["name"].lower() == product_name.lower():
            return {product_field: product.get(product_field.value)}
    raise HTTPException(status_code=404, detail="Product not found")
