"""Module responsible for scrapping Imovirtual.com"""


import json
import logging
from datetime import datetime
from typing import List, Tuple

import requests
from bs4 import BeautifulSoup

from house_collector.base_scrapper import WebsiteScrapper
from house_collector.utils import get_until_success

# pylint: disable=line-too-long

LOGGER = logging.getLogger("ImovirtualScrapper")
RESULT_PER_PAGE = 72
URL = f"https://www.imovirtual.com/en/comprar/?nrAdsPerPage={RESULT_PER_PAGE}&page=1"
URL_SEARCH = f"https://www.imovirtual.com/en/comprar/?search%5Bcreated_since%5D=<DAYS_ELAPSED>&nrAdsPerPage={RESULT_PER_PAGE}&page=1"

# pylint: enable=line-too-long

class ImovirtualScrapper(WebsiteScrapper):
    """_summary_

    Args:
        WebsiteScrapper (_type_): _description_
    """

    def get_house(self, link : str) -> Tuple[dict, datetime]:
        """
        Returns a House object with the data from the link
        """
        page = get_until_success(link)
        bs_page = BeautifulSoup(page.text, "html.parser")

        # Get Json data
        json_data = bs_page.find("script", {"id": "__NEXT_DATA__"}).text
        parsed_json = json.loads(json_data)

        # Set JSON data
        data = parsed_json["props"]["pageProps"]["ad"]

        selected_data_keys = {
            "advertType",
            "description",
            "exclusiveOffer",
            "title",
            "features",
        }

        # Get keys and remove <br> tags from description
        selected_data = {k: data[k] for k in selected_data_keys if k in data}
        selected_data["category"] = data["category"]["name"][0]["value"]
        selected_data["_id"] = data["id"]
        selected_data["description"] = (
            selected_data["description"]
            .replace("<br/>", "")
            .replace("<br>", "")
        )
        selected_data["createdAt"] = datetime.strptime(
            parsed_json["props"]["pageProps"]["ad"]["createdAt"],
            "%Y-%m-%dT%H:%M:%S%z",
        )

        # Flatten characteristics
        for characteristic_dict in data["characteristics"]:
            selected_data[characteristic_dict["key"]] = characteristic_dict[
                "value"
            ]

        # Flatten location
        selected_data["longitude"] = data["location"]["coordinates"][
            "longitude"
        ]
        selected_data["latitude"] = data["location"]["coordinates"]["latitude"]

        # Flatten address
        for key, val in data["location"]["address"].items():
            if isinstance(val, dict):
                selected_data[key] = val["name"]

        # convert "2022-09-20T12:21:43+01:00" to datetime
        modified_at = datetime.strptime(
            parsed_json["props"]["pageProps"]["ad"]["modifiedAt"],
            "%Y-%m-%dT%H:%M:%S%z",
        )

        return selected_data, modified_at

    def get_provider_name(self):
        return "imovirtual"

    def is_get_house_request(self) -> bool:
        return True

    def get_house_list(
        self,
        location: str = None,
        min_date: datetime = None,
        max_houses: int = 9999999,
    ) -> List[str]:
        """
        Returns a list of links to houses
        """

        # Set URL
        if min_date is not None:
            curr_url = URL_SEARCH.replace(
                "<DAYS_ELAPSED>", str((datetime.now() - min_date).days)
            )
        else:
            curr_url = URL

        page = requests.get(curr_url, timeout=10)
        page.raise_for_status()
        bs_data = BeautifulSoup(page.text, "html.parser")

        num_pages = int(
            bs_data.find(
                "li", {"class": "pager-next"}
            ).previous_sibling.previous_sibling.a.text
        )

        lst = []

        LOGGER.info("Scrapping %d pages", num_pages)
        for i in reversed(range(1, num_pages + 1)):
            new_url = curr_url.replace("page=1", f"page={i}")

            LOGGER.info("Scrapping page %d with URL=%s", i, new_url)

            # Make request
            page = get_until_success(new_url)

            # Parse page
            bs_data = BeautifulSoup(page.text, "html.parser")
            links = self.get_houses_links_from_page(bs_data)

            LOGGER.debug("Found %d house articles", len(links))

            lst.extend(links)

            # Make sure we don't get more than max_houses
            if len(lst) > max_houses:
                return lst[:max_houses]

        return lst

# pylint: disable=broad-except
    def get_houses_links_from_page(self, bs_data: BeautifulSoup) -> List[str]:
        """
        Get all houses URLs from a search page

        Args:
            bs_data (BeautifulSoup): _description_

        Returns:
            Set[str]: _description_
        """
        html_houses = bs_data.find_all("article")
        house_list = []
        for html_house in html_houses:
            try:
                url = html_house["data-url"]
                house_list.append(url)
            except Exception:
                LOGGER.warning("Error getting url of house")
        house_list.reverse()

        return house_list
# pylint: enable=broad-except
