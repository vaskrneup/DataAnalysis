import datetime

from bs4 import BeautifulSoup

from managers.data_extractor_manager import DataExtractorManager
from data_extractors.mixins import NepseColumnExtractorMixin, NepseTableDataExtractorMixin


class SharePriceScraper(DataExtractorManager, NepseColumnExtractorMixin, NepseTableDataExtractorMixin):
    CACHE_DATA_COUNT = 16

    def __init__(self, *args, start_date, end_date, **kwargs):
        super().__init__(*args, **kwargs)

        self.start_date = start_date
        self.end_date = end_date

        self.columns = None

    def url_generator(self) -> dict:
        time_delta = datetime.timedelta(days=1)

        while self.start_date < self.end_date:
            year, month, day = self.start_date.year, self.start_date.month, self.start_date.day
            yield {
                "url": f"http://nepalstock.com.np/todaysprice?startDate={year}-{month}-{day}&stock-symbol=&_limit=500",
                "extras": {
                    "formatted_date": f"{year}-{month}-{day}",
                    "datetime": self.start_date
                }
            }

            self.start_date = self.start_date + time_delta

    def save_data(self, data: list):
        self.write_to_csv_file(data)

    async def scrape_data(self, url: str, soup: BeautifulSoup, extras: dict):
        print(url)
        if table := soup.select("table.table.table-condensed.table-hover"):
            table = table[0]

            if self.columns is None:
                self.columns = self.get_nepse_column(
                    table,
                    pre_data=[
                        "date", "time", "weekday", "weekday_number", "symbol"
                    ]
                )

            return self.get_nepse_row_data(
                table, 2, 4,
                pre_data=[
                    extras["formatted_date"], "15:00:00",
                    extras["datetime"].strftime("%A"), extras["datetime"].weekday(),
                    lambda scraped_data: self.company_data.get_company_symbol_from_name(scraped_data[1])
                ]
            )

        return None
