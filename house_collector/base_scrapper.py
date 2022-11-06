"""
This module defines an interface that
shall be implemented by scrappers
"""
from datetime import datetime
from typing import List, Tuple


class House:
    """_summary_"""

    def parse(self):
        """
        Parse the house page

        Raises:
            NotImplementedError: _description_
        """
        raise NotImplementedError()

    def get_provider(self):
        """
        Returns the provider name to be saved on the DB
        """
        raise NotImplementedError()

    def get_title(self):
        """
        Get the title of the house
        """
        return None

    def get_description(self):
        """
        Get the description of the house
        """
        return None

    def get_bedrooms(self):
        """
        Get the number of bedrooms
        """
        return None

    def get_bathrooms(self):
        """
        Get the number of bathrooms
        """
        return None

    def get_location(self):
        """
        Get the location of the house
        """
        return None

    def get_address(self):
        """
        Get the address of the house
        """
        return None

    def get_price(self):
        """
        Get the price of the house
        """
        return None

    def get_util_area(self):
        """
        Get the util area of the house
        """
        return None

    def get_brute_area(self):
        """
        Get the brute area of the house, includes all the terrain around
        """
        return None

    def get_field_area(self):
        """
        Get the field area of the house
        """
        return None

    def get_link(self):
        """
        Get the url link of the house
        """
        return None

    def get_construction_year(self):
        """
        Get the construction year of the house
        """
        return None

    def get_energy_certificate(self):
        """
        Get the energy certificate of the house
        """
        return None

    def get_condition(self):
        """
        Get the condition of the house
        """
        return None

    def get_is_investment(self):
        """
        Get if the house is an investment
        """
        return None

    def get_json(self) -> dict:
        """
        Returns the house as a json by calling every function and removing fields that are None

        Returns:
            dict: a dictionary with the house data
        """
        json_file = {
            "title": self.get_title(),
            "topology": self.get_bedrooms(),
            "location": self.get_location(),
            "address": self.get_address(),
            "price": self.get_price(),
            "util_area": self.get_util_area(),
            "brute_area": self.get_brute_area(),
            "field_area": self.get_field_area(),
            "bathrooms": self.get_bathrooms(),
            "link": self.get_link(),
            "construction_year": self.get_construction_year(),
            "energy_certificate": self.get_energy_certificate(),
            "condition": self.get_condition(),
            "investment": self.get_is_investment(),
            "description": self.get_description(),
        }

        return {k: v for k, v in json_file.items() if v is not None}

    def __str__(self):
        return f"""Title:{self.get_title()}
Topology:{self.get_bedrooms()}
Location:{self.get_location()}
Address:{self.get_address()}
Price:{self.get_price()}
UtilArea:{self.get_util_area()}
BruteArea:{self.get_brute_area()}
FieldArea:{self.get_field_area()}
Bathrooms:{self.get_bathrooms()}
Link:{self.get_link()}
Construction Year:{self.get_construction_year()}
Energy Certificate:{self.get_energy_certificate()}
Condition:{self.get_condition()}
Investment:{self.get_is_investment()}\n"""


class WebsiteScrapper:
    """_summary_"""

    def get_house(self, link : str) -> Tuple[dict, datetime]:
        """
        This method should return a House object with the data from the link.
        It must also return the date of the last update of the house ().
        """
        raise NotImplementedError()

    def is_get_house_request(self) -> bool:
        """
        This method shall return True if the get_house method uses
        a request to get the data, False otherwise
        """
        raise NotImplementedError()

    def get_provider_name(self):
        """
        This method should return the name of the provider
        """
        raise NotImplementedError()

    def get_house_list(
        self,
        location: str = None,
        min_date: datetime = None,
        max_houses: int = 9999999,
    ) -> List[str]:
        """
        This method should return a list of links for each house according to the
        filters provided, the list should be sorted by date (oldest first)
        """
        raise NotImplementedError()
