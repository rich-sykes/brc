

"""
A tool to generate a report showing the positions and profit & loss for a hypothetical trading account.

The user should be able to choose the date they want the report to refer to.

Input Data:
TradeTable - a table with the relevant data for all the trades executed in the account
PriceData - end-of-day historical prices for each contract traded
ContractTable - a contract specification table
InstrumentTable - an instrument specification table
                (we define “instrument” a group of futures contracts which refer to the same underlying)

Reporting Parameters:
- Position held in the portfolio (in contracts)
- Valuation
- Daily P&L
- Month-to-date P&L
- Year-to-date P&L

Information should be presented in 3 levels of aggregation: Instrument asset class, instrument and contract.

The aggregation level can be an option or all three can be provided in separate tables.

"""

# init
reporting_date = "02/05/2019"


# positions held
from libs.data import get_trade_data, get_contract_data, get_price_data

import pandas as pd

trade_data = get_trade_data()

# function dev
def filter_date(trade_data, reporting_date):

    date_dt = pd.to_datetime(reporting_date, format="%d/%m/%Y")

    trade_data = trade_data[trade_data.index <= date_dt]

    return trade_data

contract_names = ["CCN9 Comdty", "CDM9 Curncy"]


def filter_contract(trade_data, contract_names):

    trade_data = trade_data[trade_data['Contract Ticker'].isin(contract_names)]

    return trade_data



def positions_held(trade_data, reporting_date):

def agg_contracts(trade_data, contract_names, date_dt):

    contract_data = get_contract_data()


    df = pd.merge(trade_data.reset_index(), contract_data[['Contract Ticker', 'Contract Multiplier']],
                  on=['Contract Ticker'])

    # daily price
    price_data = get_price_data()
    price_data = price_data[contract_names]
    price_data = price_data[contract_names][price_data.index <= date_dt]
    df_p = pd.melt(price_data.reset_index(),
                   id_vars='Date',
                   value_vars=contract_names,
                   var_name='Contract Ticker',
                   value_name='Daily Price'
                   ).set_index('Date')
    # final price
    price_data_final = price_data[contract_names][price_data.index == date_dt]
    df_pf = pd.melt(price_data_final.reset_index(),
                   id_vars='Date',
                   value_vars=contract_names,
                   var_name='Contract Ticker',
                   value_name='Final Price'
                   ).set_index('Date')



    df_merge = pd.merge(df,df_p).set_index('Trade Date')

    df_merge = pd.merge(df_merge,df_pf).set_index('Trade Date')

    # daily p/l
    # PriceChange * Multiplier * TradeAmount * IF(SELL, -1, 1)
    df_merge



