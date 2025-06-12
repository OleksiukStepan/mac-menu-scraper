import os

# Full URL to McDonald's full menu page for scraping
MAC_FULLMENU_URL = "https://www.mcdonalds.com/ua/uk-ua/eat/fullmenu.html"

# Absolute root path of the project
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# Output path for saving parsed product data in JSON format
JSON_OUTPUT_PATH = os.path.join(ROOT_DIR, "data", "products.json")


# McDonald's selectors and IDs
MENU_PRODUCT_LINK_SELECTOR = "a.cmp-category__item-link[href*='/product/']"
PRODUCT_TITLE_SELECTOR = "span.cmp-product-details-main__heading-title"
PRODUCT_DESCRIPTION_SELECTOR = ".cmp-product-details-main__description"
NUTRITION_ACCORDION_BUTTON_ID = "accordion-29309a7a60-item-9ea8a10642-button"
MAIN_NUTRITION_SELECTOR = "li.cmp-nutrition-summary__heading-primary-item"
SECONDARY_NUTRITION_SELECTOR = ".secondarynutritions li.label-item"
VALUE_SPAN_SELECTOR = "span.value span"
