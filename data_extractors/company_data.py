from bs4 import BeautifulSoup

from data_extractors.mixins import NepseColumnExtractorMixin, NepseTableDataExtractorMixin
from managers.data_extractor_manager import DataExtractorManager


class CompanyDataScraper(DataExtractorManager, NepseColumnExtractorMixin, NepseTableDataExtractorMixin):
    CACHE_DATA_COUNT = 16

    def url_generator(self) -> dict:
        yield {
            "url": "http://nepalstock.com.np/company?stock-name=&stock-symbol=&sector-id=&_limit=500",
            "extras": {}
        }

    def save_data(self, data: list):
        self.write_to_csv_file(data)

    async def scrape_data(self, url: str, soup: BeautifulSoup, extras: dict):
        if table := soup.select(".my-table.table"):
            table = table[0]

            if self.columns is None:
                self.columns = self.get_nepse_column(table)

            return self.get_nepse_row_data(table, 2, 1)

        return None
