# pylint: disable=missing-module-docstring

import logging
import time

import requests

LOGGER = logging.getLogger("utils")


def get_until_success(*args, **kwargs):
    """
    Make a get request until it succeeds
    The arguments will be passed directly to requests.get
    """
    page = requests.get(*args, **kwargs, timeout=10)
    while page.status_code != 200:
        LOGGER.warning(
            "Request failed with status code %d. Retrying...",
            page.status_code,
        )
        time.sleep(3)
        page = requests.get(*args, **kwargs, timeout=10)
    return page


def post_until_success(*args, **kwargs):
    """
    Make a post request until it succeeds
    The arguments will be passed directly to requests.post
    """
    page = requests.post(*args, **kwargs, timeout=10)
    while page.status_code != 200:
        LOGGER.warning(
            "Request failed with status code %d. Retrying...",
            page.status_code,
        )
        time.sleep(10)
        page = requests.post(*args, **kwargs, timeout=10)
    return page
