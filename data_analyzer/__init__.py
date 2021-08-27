class CandleStick:
    def __init__(
            self, no_of_transaction,
            max_price, min_price,
            closing_price, traded_shares, amount, previous_closing,
            difference_rs, difference_percentage
    ):
        self.no_of_transaction = no_of_transaction
        self.max_price = max_price
        self.min_price = min_price

        self.closing_price = closing_price
        self.traded_shares = traded_shares
        self.amount = amount
        self.previous_closing = previous_closing

        self.difference_rs = difference_rs
        self.difference_percentage = difference_percentage
