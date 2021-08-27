import csv

from data_extractors import company_data
from data_extractors import share_price


class DataGrabber:
    DATA_DIR = "data"
    SHARE_PRICE_CLASS = share_price.SharePriceScraper
    COMPANY_NAME_CLASS = company_data.CompanyDataScraper

    def __init__(self):
        self.share_price_data = {}
        self.company_name_data = {}
        self.company_key_data = {}

    @staticmethod
    def get_file_path(_class):
        return _class.get_data_file_path(_class)

    def get_csv_file_data(self, _class):
        data = []

        with open(self.get_file_path(_class), "r") as f:
            reader = csv.reader(f)

            for _, _, stock_name, symbol, sector, _ in reader:
                data.append([stock_name, symbol, sector])

        return data

    def load_company_data(self):
        for stock_name, symbol, sector in self.get_csv_file_data(self.COMPANY_NAME_CLASS):
            self.company_key_data[symbol] = {
                "stock_name": stock_name,
                "symbol": symbol
            }
            self.company_name_data[stock_name] = symbol

    def get_company_data_from_key(self, key, internal_key):
        if not self.company_key_data:
            self.load_company_data()

        if company := self.company_key_data.get(key):
            return company[internal_key]

        return None

    def get_company_data_from_name(self, name, internal_key):
        if key := self.get_company_symbol_from_name(name):
            return self.get_company_data_from_key(key, internal_key)

        return None

    def get_company_symbol_from_name(self, name):
        if not self.company_key_data:
            self.load_company_data()

        return self.company_name_data.get(name)

    def get_company_name_from_key(self, key):
        return self.get_company_data_from_key(key, "stock_name")
