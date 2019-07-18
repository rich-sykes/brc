# pypi libraries
import pandas as pd

# specific libs
from libs.ini import source_path


"""
libs.data is a pseudo data source function that will act as a substitute SQL connection

formatting of data will also be handled in this section
"""


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


# contract_Table
def get_contract_data():
    
    # import contract_table
    contract_table = pd.read_csv(source_path + "ContractTable.csv")
    
    # format contract_table
    contract_table['Instrument Code'] = contract_table['Instrument Code'].astype(int)
    contract_table['Contract Multiplier'] = contract_table['Contract Multiplier'].astype(float)
    # contract_table['Contract Description']
    contract_table['Contract Ticker'] = contract_table['Contract Ticker'].str.strip()

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


# price_data
def get_price_data():
    # import price_data
    price_data = pd.read_csv(source_path + "PriceData.csv")

    # format price_data
    price_data['Date'] = pd.to_datetime(price_data['Date'], format="%d/%m/%Y")
    price_data.set_index('Date', inplace=True, drop=True)
    price_data = price_data.apply(pd.to_numeric, args=('coerce',))

    return price_data

# eof
