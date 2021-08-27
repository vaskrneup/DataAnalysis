from data_analyzer import CandleStick


class PercentagePriceChangeMixin:
    @staticmethod
    def get_price_difference_percentage(share_price):
        percentage_diff = []

        for previous_closing, difference_rs in zip(
                share_price["previous_closing"], share_price["difference_rs"]
        ):
            try:
                percentage_diff.append(round((float(difference_rs) / float(previous_closing)) * 100, 2))
            except Exception as e:  # NOQA
                # self.logger.error(e)
                percentage_diff.append(0)

        return percentage_diff


class CandlestickPatternIdentifierMixin:
    @staticmethod
    def hammer(candles: list[CandleStick]):
        pass

    @staticmethod
    def inverted_hammer(candles: list[CandleStick]):
        pass
