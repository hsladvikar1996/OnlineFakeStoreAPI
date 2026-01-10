import shutil
import time
import pytest
from routes.Routes import Routes
from utils.ConfigReader import ReadConfig
import logging
import os
import requests


LOG_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "logs", "test_logging.log"))
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
logger = logging.getLogger("api_logger")
logger.setLevel(logging.DEBUG)

if not logger.handlers:
    file_handler = logging.FileHandler(LOG_FILE, mode="a")
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

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

    original_request = requests.Session.request

    def custom_request(self, method, url, **kwargs):
        response = original_request(self, method, url, **kwargs)
        log_request_response(response)
        return response

    requests.Session.request= custom_request


    yield {"base_url":Routes.BASE_URL, "config_reader":ReadConfig}

