from pandas import DataFrame

from data_extractors.share_price import SharePriceScraper
from managers.analysis import AnalysisManager


class StrategyValidator(AnalysisManager):
    EXTRACTOR_CLASSES: list[dict] = [
        {"class": SharePriceScraper, "data_identifier": "share_price"},
    ]

    def __init__(self):
        super(StrategyValidator, self).__init__()

        self.share_price: DataFrame = self.data["share_price"]
        self.share_price["difference_percentage"] = self.get_price_difference_percentage(self.share_price)

    def validate_first_strategy(self):
        self.logger.info(self.share_price.columns)
        return self.get_successful_message("SUCCESSFUL !!")
