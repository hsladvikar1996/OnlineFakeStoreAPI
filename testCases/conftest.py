import shutil
import time
import pytest
from routes.Routes import Routes
from utils.ConfigReader import ReadConfig
import logging
import os
import requests


LOG_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "logs", "test_logging.log"))

logger= logging.getLogger()

def log_request_response(response: requests.Response):
    req = response.request
    logger.info(f"REQUEST: {req.method} {req.url}")
    logger.info(f"Request Headers: {req.headers}")
    if req.body:
        logger.info(f"Request Body: {req.body}")
        logger.info(f"RESPONSE Status: {response.status_code}")
        logger.info(f"Response Headers: {response.headers}")
    try:
        logger.info(f"Response Body: {response.json()}")
    except Exception:
        logger.info(f"Response Body: {response.text}")



@pytest.fixture(scope= "class",autouse=True)
def setup():
    # base_url = Routes.BASE_URL
    # config_reader= ReadConfig
    # Initialize logging after cleanup
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.DEBUG,
        format="%(asctime)s | %(levelname)s | %(message)s",
        filemode='a'  # Add data to log file each run
    )
    global logger
    logger = logging.getLogger()

    original_request = requests.Session.request

    def custom_request(self, method, url, **kwargs):
        response = original_request(self, method, url, **kwargs)
        log_request_response(response)
        return response

    requests.Session.request= custom_request


    yield {"base_url":Routes.BASE_URL, "config_reader":ReadConfig}

def safe_delete_folder(folder_path, retries=3, delay=1):
    for attempt in range(retries):
        try:
            if os.path.exists(folder_path):
                shutil.rmtree(folder_path)
            return
        except PermissionError:
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                raise

@pytest.fixture(scope="session", autouse=True)
def clear_old_reports():
    # Force close all logging file handlers FIRST
    logging.shutdown()

    folders_to_clear = [
        "reports",
        "logs",
        "allure-results"
    ]

    for folder in folders_to_clear:
        try:
            safe_delete_folder(folder)
            os.makedirs(folder, exist_ok=True)
            print(f"✅ Cleared folder: {folder}")
        except Exception as e:
            print(f"⚠️ Could not clear {folder}: {e}")