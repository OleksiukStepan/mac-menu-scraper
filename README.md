# 🍔 McDonald's Menu Scraper

**MacMenuScraper** is a Python project that scrapes the full product menu from McDonald’s Ukraine:  
[https://www.mcdonalds.com/ua/uk-ua/eat/fullmenu.html](https://www.mcdonalds.com/ua/uk-ua/eat/fullmenu.html)

The project automates the collection of all product data from the site, including:
- Product name and description
- Primary nutrition information (calories, fats, carbs, proteins)
- Secondary nutrition information (unsaturated fats, sugar, salt, portion size)
- Final output saved as a JSON file

Includes full test coverage and modular architecture for scraping, data access, and API functionality.

---

## Table of Contents

1. [Project Structure](#project-structure)  
2. [Install Requirements](#install-requirements)  
3. [Run the Scraper](#run-the-scraper)
4. [Run the Api](#run-the-api)
5. [API Endpoints Overview](#api-endpoints-overview)
6. [Run Tests](#run-tests)

---

## Project Structure

```
MacMenuScraper/
├── app/
│   ├── __init__.py
│   ├── api.py            # FastAPI endpoints
│   ├── enums.py          # Enum for allowed product fields (e.g. calories, fats...)
│   ├── main.py           # FastAPI app entry point
│   └── models.py         # Pydantic models for product schema
│
├── data/
│   └── products.json     # Output file with scraped data
│
├── scraper/
│   ├── __init__.py
│   ├── parser.py         # Main parsing logic, multithreading, retries
│   └── utils.py          # WebDriver setup, helpers, and wait conditions
│
├── tests/
│   ├── __init__.py
│   ├── test_api.py       # Tests for FastAPI endpoints
│   └── test_scraper.py   # Tests for scraper functionality
│
├── config.py             # Constants (URL, paths, selectors)
├── .gitignore            # Ignored files and folders
├── requirements.txt      # Project dependencies
└── README.md             # Project documentation
```

---

## Install Requirements

```bash
pip install -r requirements.txt
```

---

## Run the Scraper

To collect all products and save them into JSON:

```bash
python scraper/parser.py
```

The result will be saved in:

```
data/products.json
```

---

## Run the API

> ⚠️ Make sure to run the scraper before starting the API!

To start the FastAPI server:

```bash
uvicorn app.main:app --reload
```

Once running, the API will be available at:

```
http://127.0.0.1:8000
```

You can explore all available endpoints in the interactive docs:

- Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## API Endpoints Overview

### Get all products
```
GET /products/
```

### Get a product by name
```
GET /products/{product_name}
```

### Get a specific field of a product
```
GET /products/{product_name}/{field}
```

Where `field` can be one of:

```
description | calories | fats | carbs | proteins | 
unsaturated_fats | sugar | salt | portion
```

---

## Run Tests

> ⚠️ Ensure that dependencies are installed and `data/products.json` is present

To run all unit tests:

```bash
pytest
```
