import logging
import re

from fake_useragent import UserAgent
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait

from config import VALUE_SPAN_SELECTOR


def init_driver():
    """Initialize headless Chrome WebDriver"""
    options = Options()
    ua = UserAgent()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--blink-settings=imagesEnabled=false")
    options.add_argument(f"user-agent={ua.random}")
    return webdriver.Chrome(options=options)


def wait_for_nutrition_loading(
    driver: WebDriver,
    selector: str,
    timeout: int = 10
) -> bool:
    """
    Wait for nutrition values to appear under given selector.
    Returns True if content is loaded and not empty, False otherwise.
    """
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: d.find_elements(
                By.CSS_SELECTOR, f"{selector} {VALUE_SPAN_SELECTOR}"
            ) and any(
                el.text.strip()
                for el in d.find_elements(
                    By.CSS_SELECTOR, f"{selector} {VALUE_SPAN_SELECTOR}"
                )
            )
        )
        return True
    except TimeoutException:
        logging.warning(
            f"Nutrition block '{selector}' failed to load in {timeout}s"
        )
        return False


def extract_float(text: str) -> float | None:
    """
    Extract first float from text like '24г' or 'N/A', return None if not valid
    """
    if not text:
        return None

    first = text.strip().split(" ")[0].lower()
    if first.startswith(("n/a", "н/а", "-", "—")):
        return None

    match = re.search(r"[\d.]+", text.replace(",", "."))
    return float(match.group()) if match else None


def chunkify(lst: list[str], n: int) -> list[list[str]]:
    """Split list into n chunks"""
    return [lst[i::n] for i in range(n)]
