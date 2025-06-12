import json
import logging
import os
import time

from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from app.models import Product
from config import (
    JSON_OUTPUT_PATH,
    MAC_FULLMENU_URL,
    MENU_PRODUCT_LINK_SELECTOR,
    PRODUCT_TITLE_SELECTOR,
    PRODUCT_DESCRIPTION_SELECTOR,
    MAIN_NUTRITION_SELECTOR,
    SECONDARY_NUTRITION_SELECTOR,
    VALUE_SPAN_SELECTOR,
    NUTRITION_ACCORDION_BUTTON_ID,
)
from scraper.utils import (
    chunkify,
    init_driver,
    extract_float,
    wait_for_nutrition_loading,
)

# Logging config
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def collect_product_urls(driver: WebDriver) -> list[str]:
    """Collect all product URLs from the full menu page"""
    driver.get(MAC_FULLMENU_URL)
    WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, MENU_PRODUCT_LINK_SELECTOR)
        )
    )
    product_links = driver.find_elements(
        By.CSS_SELECTOR,
        MENU_PRODUCT_LINK_SELECTOR
    )

    return [link.get_attribute("href") for link in product_links]


def parse_all_products_concurrently(
        urls: list[str],
        max_workers: int = 5
) -> list[Product]:
    """Parse products concurrently with isolated drivers"""
    chunks = chunkify(urls, max_workers)
    all_products = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(worker_process_urls, chunk, idx): idx
            for idx, chunk in enumerate(chunks)
        }

        for future in as_completed(futures):
            try:
                products = future.result()
                all_products.extend(products)
            except Exception as e:
                logging.error(f"Worker-{futures[future]} failed: {e}")

    return all_products


def parse_product_with_driver(url: str) -> Product | None:
    """Creates isolated driver for single product and parses it with retries"""
    driver = init_driver()
    try:
        return parse_product_with_retries(url, driver)
    except Exception as e:
        logging.error(f"Critical failure for {url}: {e}")
        return None
    finally:
        driver.quit()


def worker_process_urls(urls: list[str], worker_id: int = 0) -> list[Product]:
    """Each worker gets its own driver and parses a list of URLs"""
    logging.info(f"Worker-{worker_id} started with {len(urls)} URLs")
    driver = init_driver()
    results = []

    for url in urls:
        try:
            product = parse_product_with_retries(url, driver)
            if product:
                results.append(product)
                logging.info(f"[Worker-{worker_id}] Parsed: {url}")
        except Exception as e:
            logging.error(f"[Worker-{worker_id}] Error: {e}")

    driver.quit()
    logging.info(f"Worker-{worker_id} finished")
    return results


def parse_product_with_retries(
        url: str,
        driver: WebDriver,
        max_retries=3
) -> Product | None:
    """Attempt to parse a single product URL with retry logic"""
    for attempt in range(max_retries):
        try:
            product = parse_product(url, driver)
            if product:
                return product
        except Exception as e:
            logging.warning(f"Retry {attempt+1} failed for {url}: {e}")
            time.sleep(2)
    logging.error(f"Failed to parse {url} after {max_retries} retries")
    return None


def parse_product(url: str, driver: WebDriver) -> Product | None:
    """Parse full nutritional info from a single McDonald's product page"""
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, PRODUCT_TITLE_SELECTOR))
        )

        name = driver.find_element(
            By.CSS_SELECTOR, PRODUCT_TITLE_SELECTOR
        ).get_attribute("textContent").strip()
        description = driver.find_element(
            By.CSS_SELECTOR, PRODUCT_DESCRIPTION_SELECTOR
        ).text.strip()

        expand_nutrition_section(driver)

        main_nutrition = parse_main_nutrition(driver)
        secondary_nutrition = parse_secondary_nutrition(driver)

        return Product(
            name=name,
            description=description,
            calories=main_nutrition["calories"],
            fats=main_nutrition["fats"],
            carbs=main_nutrition["carbs"],
            proteins=main_nutrition["proteins"],
            unsaturated_fats=secondary_nutrition["unsaturated_fats"],
            sugar=secondary_nutrition["sugar"],
            salt=secondary_nutrition["salt"],
            portion=secondary_nutrition["portion"]
        )
    except Exception as e:
        logging.error(f"Failed to parse product at {url}: {e}")
        return None


def parse_main_nutrition(driver: WebDriver) -> dict[str, float | None]:
    """Parse main nutrients: calories, fats, carbs, proteins"""
    return parse_nutrition_section(
        driver,
        selector=MAIN_NUTRITION_SELECTOR,
        expected_fields=["calories", "fats", "carbs", "proteins"]
    )


def parse_secondary_nutrition(driver: WebDriver) -> dict[str, float | None]:
    """Parse secondary nutrients: unsaturated fats, sugar, salt, portion"""
    return parse_nutrition_section(
        driver,
        selector=SECONDARY_NUTRITION_SELECTOR,
        expected_fields=["unsaturated_fats", "sugar", "salt", "portion"]
    )


def parse_nutrition_section(
        driver,
        selector: str,
        expected_fields: list
) -> dict:
    """Generic parser for nutrition blocks (main/secondary)"""
    if not wait_for_nutrition_loading(driver, selector):
        return {field: None for field in expected_fields}

    items = driver.find_elements(By.CSS_SELECTOR, selector)
    results = {}

    for index, field in enumerate(expected_fields):
        try:
            value_element = items[index].find_element(
                By.CSS_SELECTOR, VALUE_SPAN_SELECTOR
            )
            text = value_element.text.strip()
            results[field] = extract_float(text)
        except Exception as e:
            logging.warning(f"Could not parse {field}: {e}")
            results[field] = None

    return results


def expand_nutrition_section(driver: WebDriver) -> None:
    """Waits for the nutrition accordion button to appear and clicks it"""
    accordion_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, NUTRITION_ACCORDION_BUTTON_ID))
    )
    driver.execute_script(
        "arguments[0].scrollIntoView({block: 'center'});",
        accordion_button
    )
    time.sleep(1)

    try:
        accordion_button.click()
    except Exception:
        driver.execute_script(
            "arguments[0].click();",
            accordion_button
        )


def save_products_to_json(products: list[Product], filepath: str) -> None:
    """Save parsed products to a JSON file"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(
            [p.model_dump() for p in products],
            file,
            ensure_ascii=False,
            indent=2
        )
    logging.info(f"Saved {len(products)} products to {filepath}")


def main() -> None:
    """
       Entry point:
       1. Collects product URLs from McDonald's full menu page.
       2. Parses each product concurrently using separate WebDrivers.
       3. Saves all results to a JSON file.
    """
    main_driver = init_driver()
    try:
        logging.info("Collecting product URLs...")
        product_urls = collect_product_urls(main_driver)
    except Exception as e:
        logging.error(f"Failed to collect product URLs: {e}")
        return
    finally:
        main_driver.quit()

    logging.info(
        f"Found {len(product_urls)} products. Starting parallel parsing..."
    )

    products = parse_all_products_concurrently(product_urls, max_workers=5)
    save_products_to_json(products, JSON_OUTPUT_PATH)

    logging.info("Parsing completed")


if __name__ == "__main__":
    main()
