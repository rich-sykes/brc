"""
libs.data is a pseudo data source function that will act as a substitute SQL connection

formatting of data will also be handled in this section
"""

# pypi libraries
import pandas as pd
from pandas.tseries.offsets import MonthEnd

# specific libs
from libs.ini import source_path


# instrument_table
def get_instrument_data():

    # import instrument_table
    instrument_table = pd.read_csv(source_path + "InstrumentTable.csv")
    
    # format instrument_table
    instrument_table['Instrument Code'] = instrument_table['Instrument Code'].astype(int)
    instrument_table['Instrument Description'] = instrument_table['Instrument Description'].str.strip()
    instrument_table['Instrument Asset Class'] = instrument_table['Instrument Asset Class'].str.strip()
    instrument_table['Instrument Currency'] = instrument_table['Instrument Currency'].str.strip()
    instrument_table['Instrument Currency'] = instrument_table['Instrument Currency'].str.upper()

    return instrument_table


# price_data
def get_price_data():

    # import price_data
    price_data = pd.read_csv(source_path + "PriceData.csv")

    # format price_data
    price_data['Date'] = pd.to_datetime(price_data['Date'], format="%d/%m/%Y")
    price_data.set_index('Date', inplace=True, drop=True)
    price_data = price_data.apply(pd.to_numeric, args=('coerce',))

    return price_data


# contract_Table
def get_contract_data():
    
    # import contract_table
    contract_table = pd.read_csv(source_path + "ContractTable.csv")

    # format contract_table
    contract_table['Instrument Code'] = contract_table['Instrument Code'].astype(int)
    contract_table['Contract Multiplier'] = contract_table['Contract Multiplier'].astype(float)
    contract_table['Contract Ticker'] = contract_table['Contract Ticker'].str.strip()

    contract_table['Contract Expiry'] = contract_table['Contract Description'].str.extract('([A-Z]{1}[a-z]{2}[0-9]{2})',
                                                                                           expand=True)

    # init expiry date with month end
    contract_table['Contract Expiry'] = pd.to_datetime(contract_table['Contract Expiry'], format="%b%y") + MonthEnd(1)

    price_data = get_price_data()

    # list of contract tickers
    contract_tickers = contract_table['Contract Ticker'].tolist()

    # get last valid date (assumption for expiry date)
    expiry_date = [price_data[item].last_valid_index() for item in contract_tickers]

    contract_expiry = pd.DataFrame(list(zip(contract_tickers, expiry_date)),
                                   columns=['Contract Ticker', 'Contract Expiry'])

    # merge contract data with expiry
    contract_table = pd.merge(
        contract_table[['Contract Ticker', 'Contract Description', 'Instrument Code','Contract Multiplier']],
        contract_expiry, on='Contract Ticker')

    """
    contract_table.loc[contract_table['Contract Ticker'] == 'CDM9 Curncy', 'Contract Expiry'] \
        = pd.to_datetime("18/06/2019", format="%d/%m/%Y")

    contract_table.loc[contract_table['Contract Ticker'] == 'ESM9 Index', 'Contract Expiry'] \
        = pd.to_datetime("21/06/2019", format="%d/%m/%Y")

    contract_table.loc[contract_table['Contract Ticker'] == 'JYM9 Curncy', 'Contract Expiry'] \
        = pd.to_datetime("17/06/2019", format="%d/%m/%Y")

    contract_table.loc[contract_table['Contract Ticker'] == 'MESM9 Index', 'Contract Expiry'] \
        = pd.to_datetime("21/06/2019", format="%d/%m/%Y")

    contract_table.loc[contract_table['Contract Ticker'] == 'RTYM9 Index', 'Contract Expiry'] \
        = pd.to_datetime("21/06/2019", format="%d/%m/%Y")

    contract_table.loc[contract_table['Contract Ticker'] == 'TYM9 Comdty', 'Contract Expiry'] \
        = pd.to_datetime("19/06/2019", format="%d/%m/%Y")

    contract_table.loc[contract_table['Contract Ticker'] == 'USM9 Comdty', 'Contract Expiry'] \
        = pd.to_datetime("19/06/2019", format="%d/%m/%Y")
    """

    return contract_table


# trade_table
def get_trade_data():

    # import trade_table
    trade_table = pd.read_csv(source_path + "TradeTable.csv")
    
    # format trade_table
    trade_table['Trade Date'] = pd.to_datetime(trade_table['Trade Date'], format="%d/%m/%Y")
    trade_table.set_index('Trade Date', inplace=True, drop=True)

    trade_table['Contract Ticker'] = trade_table['Contract Ticker'].str.strip()
    trade_table['Traded Amount'] = trade_table['Traded Amount'].astype(float)
    trade_table['Avg Price Traded'] = trade_table['Avg Price Traded'].astype(float)

    return trade_table

# eof
