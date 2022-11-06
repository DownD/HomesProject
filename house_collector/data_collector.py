"""
Main module responsible for collecting the data from
the multiple scrappers and send to the database
"""
import logging
import math
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from typing import List, Set

from house_collector.base_scrapper import WebsiteScrapper
from house_collector.db_handler import DBHandler
from house_collector.imovirtual_scrapper import ImovirtualScrapper
from house_collector.olx_scrapper import OlxScrapper

SCRAPPER_LIST: Set[WebsiteScrapper] = {ImovirtualScrapper(), OlxScrapper()}
LOGGER = logging.getLogger("DataCollector")


class DataCollector:
    """
    DataCollector class

    Remarks:
    Although pymongo is thread safe, the DBHandler is not as it does some checks
    before importing a house.
    If 2 threads try to import the same house at the same time, the DBHandler could fail.
    As this is considered a very rare case, this problem was ignored and remains to be fixed in the future.
    """

    def __init__(self, db_host, db_port, max_threads: int = 100, use_threading: bool = True, check_interval_min: int = 30):
        """
        Constructor

        Args:
            max_threads (int, optional): The maximum number of threads to be used. Defaults to 100.
        """
        self.db_handler = DBHandler(host=db_host, port=db_port)
        self.scrapper_list = SCRAPPER_LIST
        self.max_threads = max_threads
        self.use_threading = use_threading
        self.check_interval_min = check_interval_min

        LOGGER.info("DataCollector initialized with %d threads and multi-threading=%d", max_threads, use_threading)

    def run(self):
        """
        Run the DataCollector without returning
        """
        counter = 0
        while True:
            LOGGER.info("Starting run %d", counter)
            start_time = time.time()
            self.run_once()

            LOGGER.info("The run took %s", str(timedelta(seconds=time.time() - start_time)))
            LOGGER.info("Sleeping for %d minutes", self.check_interval_min)
            counter +=1
            time.sleep(self.check_interval_min*60)

    def run_once(self):
        """
        Run the DataCollector once
        """
        for scrapper in self.scrapper_list:
            self.process_scrapper(scrapper)

    def request_pool(self, house_list: List[str], scrapper: WebsiteScrapper):
        """
        Request a pool of houses from a scrapper
        Thread safe function

        Args:
            house_list (List[str]): List of houses to request
            scrapper (WebsiteScrapper): Scrapper to request the pool
        """
        # pylint: disable=broad-except
        LOGGER.info(
            "Requesting %d houses from %s",
            len(house_list),
            scrapper.get_provider_name(),
        )
        for house_link in house_list:
            LOGGER.debug("Processing house %s", house_link)
            try:
                house, date = scrapper.get_house(house_link)  # type: ignore
                house["date_modified"] = date  # type: ignore
                house["link"] = house_link  # type: ignore
                house["available"] = True  # type: ignore

                if "_id" not in house:
                    house["_id"] = house_link  # type: ignore

                self.db_handler.insert_house(house, scrapper.get_provider_name())  # type: ignore
            except Exception as _e:
                LOGGER.exception(
                    "Error processing house %s with exception",
                    house_link,
                    # str(_e),
                )
        # pylint: enable=broad-except

    def process_scrapper(self, scrapper: WebsiteScrapper):
        """
        Process a scrapper

        Args:
            scrapper (WebsiteScrapper): Scrapper to process
        """
        LOGGER.info("Processing %s", scrapper.get_provider_name())

        latest_house = self.db_handler.get_latest_house(
            scrapper.get_provider_name()
        )

        if not latest_house:
            LOGGER.info(
                "No houses in database for %s", scrapper.get_provider_name()
            )
            house_list = scrapper.get_house_list()
        else:
            LOGGER.info(
                "Latest house in database for %s from %s",
                scrapper.get_provider_name(),
                latest_house["date_modified"],
            )
            house_list = scrapper.get_house_list(
                min_date=latest_house["date_modified"]
            )

        with open("house_cache_list.txt", "w", encoding="utf-8") as file:
            for house in house_list:
                file.write(f"{house}\n")

        LOGGER.info("Found %d houses", len(house_list))
        LOGGER.info("Houses written to house_cache_list.txt")

        if scrapper.is_get_house_request() and self.use_threading:
            # If the scrapper does get requests per house,
            # use multiple threads to make the requests

            # Make sure to not spawn more threads than houses
            if self.max_threads > len(house_list):
                tmp_threads = len(house_list)
            else:
                tmp_threads = self.max_threads

            LOGGER.info(
                "Processing %d Houses with %d threads",
                len(house_list),
                tmp_threads,
            )

            size_chunks = math.ceil(len(house_list) / tmp_threads)

            with ThreadPoolExecutor(max_workers=tmp_threads) as executor:
                chunks = [
                    house_list[offset : offset + 100]
                    for offset in range(0, len(house_list), size_chunks)
                ]
                executor.map(self.request_pool, chunks)
        else:
            LOGGER.info("Processing %d Houses with 1 thread", len(house_list))
            self.request_pool(house_list, scrapper)

        LOGGER.info("Finished processing %s", scrapper.get_provider_name())
