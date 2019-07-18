import unittest

from libs.data import get_contract_data, get_trade_data, get_price_data, get_instrument_data


class TestData(unittest.TestCase):

    # check all contracts in trade_table exist in contract_table
    def test_ticker_contract_trade(self):

        contract_data = get_contract_data()
        trade_data = get_trade_data()

        defined_tickers = contract_data['Contract Ticker'].unique().tolist()
        traded_tickers = trade_data['Contract Ticker'].unique().tolist()
        all_tickers_defined = set(traded_tickers).issubset(defined_tickers)

        self.assertTrue(all_tickers_defined)

    # check all contracts in trade_table exist in price_table
    def test_ticker_trade_price(self):
        price_data = get_price_data()
        trade_data = get_trade_data()

        price_tickers = price_data.columns.unique().tolist()
        traded_tickers = trade_data['Contract Ticker'].unique().tolist()
        all_tickers_defined = set(traded_tickers).issubset(price_tickers)

        self.assertTrue(all_tickers_defined)

    # check all contracts in contract_table exist in instrument_table
    def test_code_instrument_contract(self):
        instrument_data = get_instrument_data()
        contract_data = get_contract_data()

        instrument_codes = instrument_data['Instrument Code'].unique().tolist()
        contract_codes = contract_data['Instrument Code'].unique().tolist()
        all_codes_defined = set(contract_codes).issubset(instrument_codes)

        self.assertTrue(all_codes_defined)


if __name__ == '__main__':
    unittest.main()