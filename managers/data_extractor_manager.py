import asyncio
import csv
import os
import time

import aiohttp
from bs4 import BeautifulSoup

sem = asyncio.Semaphore(64)


class DataExtractorManager:
    MIDDLEWARES = []
    CACHE_DATA_COUNT = None
    DEFAULT_DATA_FOLDER = "data"
    SCRAPER_NAME = None

    def __init__(
            self, url_generator=None, max_concurrent_request=8, loop=None,
            request_args=None, request_kwargs=None, cache_data_count=None,
            company_data=None
    ):
        cache_data_count = self.CACHE_DATA_COUNT if cache_data_count is None else cache_data_count

        self.url_generator = self.url_generator() if url_generator is None else url_generator
        self.max_concurrent_request = max_concurrent_request
        self.loop = asyncio.get_event_loop() if loop is None else loop

        self.filename = self.get_data_file_path(self.__class__)

        self.request_args = () if request_args is None else request_args
        self.request_kwargs = {} if request_kwargs is None else request_kwargs

        self.cached_data = []
        self.cache_data_count = self.max_concurrent_request if cache_data_count is None else cache_data_count

        self.columns = None

        self.number_of_urls_scraped = 0
        self.start_time = time.time()

        self.company_data = company_data

    @staticmethod
    def get_data_file_path(_class):
        filename = (
            _class.SCRAPER_NAME
            if _class.SCRAPER_NAME else
            _class.__name__
        )
        return f"{_class.DEFAULT_DATA_FOLDER}/{filename}.csv"

    def get_script_stats(self):
        time_diff = time.time() - self.start_time

        if time_diff > 60:
            rate_per_minute = round(self.number_of_urls_scraped / time_diff * 60, 2)
            return (
                f"\u001b[32m"
                f"RATE: {rate_per_minute} / min, TOTAL URL SCRAPED: {self.number_of_urls_scraped}"
                f"\u001b[0m"
            )
        else:
            return ""

    def write_to_csv_file(self, data):
        data_file_exists = os.path.exists(self.filename)

        with open(self.filename, "a", newline="") as f:
            writer = csv.writer(f)

            if not data_file_exists:
                writer.writerow(self.columns)

            for rows in data:
                writer.writerows(rows)

    def _save_data(self, data: list):
        self.cache_data(data)

        if len(self.cached_data) >= self.cache_data_count:
            self.save_data(self.cached_data)
            self.clear_cached_data()

    def save_data(self, data: list):
        raise NotImplementedError

    def cache_data(self, data: list):
        self.number_of_urls_scraped += len(data)
        self.cached_data += [sub_data for sub_data in data if sub_data]

    def clear_cached_data(self):
        self.cached_data = []

    @staticmethod
    async def default_on_success(_resp):
        return await _resp.text()

    def url_generator(self) -> dict:
        pass

    async def request(self, method, url, on_success=None, *args, **kwargs):

        args = (*self.request_args, *args)
        kwargs = {**self.request_kwargs, **kwargs}
        on_success = self.default_on_success if on_success is None else on_success

        async with aiohttp.ClientSession() as session:
            async with sem:
                async with (
                        session.get(
                            url, *args, **kwargs
                        ) if method.upper() == "GET" else session.post(
                            url, *args,
                            **kwargs
                        )
                ) as resp:
                    return await on_success(resp)

    async def get(self, url, on_success=None, *args, **kwargs):
        return await self.request("GET", url, on_success=on_success, *args, **kwargs)

    async def post(self, url, on_success=None, *args, **kwargs):
        return await self.request("POST", url, on_success=on_success, *args, **kwargs)

    async def get_html(self, url, *args, **kwargs):
        return await self.get(url, *args, **kwargs)

    async def get_soup(self, url=None, html=None, *args, **kwargs):
        if url is not None:
            html = await self.get_html(url, *args, **kwargs)
        elif html is not None:
            html = html
        else:
            html = ""
            assert True, "Both html and url cant be None"
        return BeautifulSoup(html, "lxml")

    async def scrape_data(self, url: str, soup: BeautifulSoup, extras: dict):
        raise NotImplementedError

    async def scrape(self):
        for urls in self.get_next_url_sequence():
            urls = list(urls)
            soups = await asyncio.gather(*(self.get_soup(url["url"]) for url in urls))
            data = await asyncio.gather(
                *(self.scrape_data(url["url"], soup, url["extras"]) for url, soup in zip(urls, soups))
            )
            self._save_data(list(data))
            print(self.get_script_stats())

        if self.cached_data:
            self.save_data(self.cached_data)

    def get_next_url_sequence(self):
        data = []

        for url in self.url_generator:
            data.append(url)

            if len(data) >= self.max_concurrent_request:
                yield data
                data = []

        if data:
            yield data

    def __call__(self, *args, **kwargs):
        self.loop.run_until_complete(self.scrape())
