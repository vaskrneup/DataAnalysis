import datetime

from config.config import Config
from data_extractors import share_price
from managers.data_grabber_manager import DataGrabber
# from data_analyzer.strategy_validator import StrategyValidator

# company_data = DataGrabber()
#
# share_price.SharePriceScraper(
#     start_date=datetime.date(day=1, month=1, year=2009),
#     end_date=datetime.date(day=20, month=7, year=2021),
#     max_concurrent_request=9,
#     company_data=company_data,
#     request_kwargs={
#         "timeout": 180
#     }
# )()
# company_data.CompanyDataScraper()()
# StrategyValidator()()
from third_party_services.meroshare.meroshare import MeroShare
from utils.pretty_print import pretty_print

config = Config()

x = MeroShare(
    config=config,
    dp=config.meroshare_credentials.get("dp"),
    username=config.meroshare_credentials.get("username"),
    password=config.meroshare_credentials.get("password"),
    pin=config.meroshare_credentials.get("pin")
).login()
# print(pretty_print(x.get_current_holdings_short_names()))
# print("=====" * 10)

# print(pretty_print(x.boid))
# print("=====" * 10)

# print(pretty_print(x.bank_data))
# print("=====" * 10)

# print(pretty_print(x.bank_code))
# print("=====" * 10)

# print(pretty_print(x.crn))
# print("=====" * 10)

# print(pretty_print(x.get_shares_holdings()))
# print("=====" * 10)

# print(pretty_print(x.get_portfolio_holdings()))
# print("=====" * 10)
#
# print(pretty_print(x.get_purchase_source("NRIC")))
# print("=====" * 10)

print(pretty_print(x.get_current_issue()))
print("=====" * 10)
