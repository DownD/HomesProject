"""Module responsible for scrapping Imovirtual.com"""

import logging
from datetime import datetime
from typing import List, Tuple

import requests

from house_collector.base_scrapper import WebsiteScrapper
from house_collector.utils import get_until_success

# pylint: disable=line-too-long

LOGGER = logging.getLogger("OlxScrapper")
RESULT_PER_PAGE = 40
URL = f"https://www.olx.pt/api/v1/offers/?offset=0&limit={RESULT_PER_PAGE}&category_id=16&sort_by=created_at%3Adesc"

# pylint: enable=line-too-long


class OlxScrapper(WebsiteScrapper):
    """_summary_

    Args:
        WebsiteScrapper (_type_): _description_
    """

    def __init__(self):
        super().__init__()
        self.houses = {}

    def get_house(self, link: str) -> Tuple[dict, datetime]:
        """
        Returns a House object with the data from the link
        """

        # Get Json data
        if link not in self.houses:
            raise ValueError(f"Link {link} not found in houses")

        data = self.houses[link]

        selected_data_keys = {
            "id",
            "title",
            "last_refresh_time",
            "created_time",
            "valid_to_time",
            "pushup_time",
            "description",
            "status",
        }

        # Get keys and remove <br> tags from description
        selected_data = {k: data[k] for k in selected_data_keys if k in data}
        selected_data["_id"] = data["id"]
        selected_data["description"] = (
            selected_data["description"]
            .replace("<br/>", "")
            .replace("<br>", "")
        )

        # Flatten promotions
        for key, val in data["promotion"].items():
            if key not in ("options", "b2c_ad_page"):
                selected_data[key] = val

        # Flatten params
        for param_dict in data["params"]:

            if "value" in param_dict["value"]:
                selected_data[param_dict["key"]] = param_dict["value"]["value"]
            elif "key" in param_dict["value"]:
                selected_data[param_dict["key"]] = param_dict["value"]["key"]
            else:
                LOGGER.warning(
                    "Param %s cannot be parsed for %s", param_dict["key"], link
                )

        # Flatten user
        selected_data["user_id"] = data["user"]["id"]
        selected_data["user_created_at"] = data["user"]["created"]

        # Flatten coords
        if "map" in data:
            selected_data["longitude"] = data["map"]["lat"]
            selected_data["latitude"] = data["map"]["lon"]

        # Flatten address
        for key, val in data["location"].items():
            if isinstance(val, dict):
                selected_data[key] = val["name"]
            else:
                LOGGER.warning("Address %s cannot be parsed for %s", key, link)

        # Flatten images
        selected_data["photos"] = [photo["link"] for photo in data["photos"]]

        # Flatten category
        for key, val in data["category"].items():
            selected_data["category_" + key] = val

        # convert to datetime
        selected_data["last_refresh_time"] = datetime.strptime(
            selected_data["last_refresh_time"], "%Y-%m-%dT%H:%M:%S%z"
        )
        selected_data["created_time"] = datetime.strptime(
            selected_data["created_time"], "%Y-%m-%dT%H:%M:%S%z"
        )
        selected_data["valid_to_time"] = datetime.strptime(
            selected_data["valid_to_time"], "%Y-%m-%dT%H:%M:%S%z"
        )
        selected_data["pushup_time"] = datetime.strptime(
            selected_data["pushup_time"], "%Y-%m-%dT%H:%M:%S%z"
        )

        # Add provider name
        selected_data["provider"] = self.get_provider_name()

        # Add link
        selected_data["link"] = link

        return selected_data, selected_data["created_time"]

    def get_provider_name(self):
        return "olx"

    def is_get_house_request(self) -> bool:
        return False

    def get_house_list(
        self,
        location: str = None,
        min_date: datetime = None,
        max_houses: int = 9999999,
    ) -> List[str]:
        """
        Returns a list of links to houses
        """

        if min_date is not None:
            LOGGER.warning("min_date is not supported for OlxScrapper, thus it will be ignored")
        
        self.houses = {}
        curr_url = URL

        page = requests.get(curr_url, timeout=10)
        page.raise_for_status()

        json_data = page.json()

        num_elements = json_data["metadata"]["visible_total_count"]
        num_pages = num_elements // RESULT_PER_PAGE + 1
        lst = []

        LOGGER.info("Scrapping %d pages", num_pages)
        for i in reversed(range(1, num_pages)):
            new_url = curr_url.replace(
                "offset=0", f"offset={i*RESULT_PER_PAGE}"
            )

            LOGGER.info("Scrapping page %d with URL=%s", i, new_url)

            # Make request
            page = get_until_success(new_url)

            # Parse page
            page_json = page.json()

            LOGGER.debug("Found %d house articles", len(page_json["data"]))

            for house in page_json["data"]:
                lst.append(house["url"])
                self.houses[house["url"]] = house

            # Make sure we don't get more than max_houses
            if len(lst) > max_houses:
                return lst[:max_houses]

        return lst
