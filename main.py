

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

Information should be presented in 3 levels of aggregation:
- Instrument asset class
- instrument
- contract

The aggregation level can be an option or all three can be provided in separate tables.

"""


import pandas as pd
from libs.data import get_instrument_data, get_contract_data, get_trade_data, get_price_data
from libs.portfolio_func import calc_daily_return, calc_contracts_held, calc_valuation
from libs.portfolio_func import calc_daily_aggregate, calc_mtd_aggregate, calc_ytd_aggregate

# aggregation filter
# aggregation_level = 'Instrument Asset Class'
# aggregation_level = 'Instrument Description'
# aggregation_level = 'Contract Ticker'

# example dates
# reporting_date = '17/06/2019'
# reporting_date = '07/06/2019'
# reporting_date = '20/06/2019'

def agg_contracts(reporting_date, aggregation_level):

    """
    # instrument_asset_classes = instrument_data['Instrument Asset Class'].unique().tolist()
    # i.e. 'Equity' / 'Commidities'
    instrument_asset_class = 'Commodities'
    instrument_codes = instrument_data[instrument_data['Instrument Asset Class'] == instrument_asset_class]['Instrument Code'].tolist()
    contract_data = get_contract_data()
    contract_tickers = contract_data[contract_data['Instrument Code'].isin(instrument_codes)]['Contract Ticker'].to_list()

    # aggregation filter  - instruments
    instrument_description = 'Russel 2000'
    instrument_codes = instrument_data[instrument_data['Instrument Description'] == instrument_description]['Instrument Code'].tolist()
    contract_tickers = contract_data[contract_data['Instrument Code'].isin(instrument_codes)]['Contract Ticker'].to_list()

    # aggregation filter  - contract or contracts
    contract_tickers = ["CCN9 Comdty", "CDM9 Curncy"]
    """

    # import data
    # TODO: pass date as optional argument to data functions
    instrument_data = get_instrument_data()
    contract_data = get_contract_data()
    trade_data = get_trade_data()
    price_data = get_price_data()


    # date functions
    current_date = pd.to_datetime(reporting_date, format="%d/%m/%Y")

    # if weekend shift to weekday
    while current_date.dayofweek > 4:
        current_date = current_date - pd.Timedelta(days=1)


    price_data_pivot = price_data.reset_index().melt(id_vars='Date',
                                                     var_name='Contract Ticker',
                                                     value_name='Price').set_index('Date')

    # filter to date of report (remnove future trades)
    price_data_pivot = price_data_pivot[price_data_pivot.index <= current_date]
    trade_data = trade_data[trade_data.index <= current_date]

    df = pd.merge(price_data_pivot.reset_index(), trade_data.reset_index(),
                  left_on=['Contract Ticker', 'Date'],
                  right_on=['Contract Ticker', 'Trade Date'],
                  how='left')

    # enrich with contract info
    df = pd.merge(df,
                  contract_data[['Contract Ticker', 'Contract Description', 'Instrument Code', 'Contract Multiplier',
                                 'Contract Expiry']],
                  on=['Contract Ticker'],
                  how='left')

    # contract expired flag
    df['Expired'] = 0
    df['Expired'][current_date >= df['Contract Expiry']] = 1

    # enrich with instrument info
    df = pd.merge(df,
                  instrument_data[[
                      'Instrument Code', 'Instrument Description', 'Instrument Asset Class', 'Instrument Currency']],
                  on=['Instrument Code'], how='left')

    df = df.sort_values(['Date', 'Contract Ticker']).set_index('Date')

    # --- df has all data and meta data ---
    df = df

    # calculate rolling PnL and valulation - contract ticker
    daily_df = calc_daily_return(df)

    # calculate value on reporting date
    value_df = calc_valuation(daily_df, current_date, aggregation_level)

    # calculate contracts held on reporting date
    holding_df = calc_contracts_held(daily_df, current_date)

    # daily PnL
    daily_pnl_df = calc_daily_aggregate(daily_df, current_date, aggregation_level)

    # monthly PnL
    month_pnl_df = calc_mtd_aggregate(daily_df, current_date, aggregation_level)

    # year_pnl_df
    year_pnl_df = calc_ytd_aggregate(daily_df, current_date, aggregation_level)


    # output data -  dictionary
    output = {}

    # Daily P&L
    output['daily'] = daily_pnl_df

    # Month-to-date P&L
    output['month'] = month_pnl_df

    # Year-to-date P&L
    output['year'] = year_pnl_df

    # Valuation
    # output['value'] = df_value[['Final Value']]
    output['value'] = value_df

    # Position held in the portfolio (in contracts)
    output['contracts'] = holding_df

    return output

# output = agg_contracts(reporting_date='20/06/2019', aggregation_level='Instrument Asset Class')
# output = agg_contracts(current_date, 'Instrument Description')
# output = agg_contracts(current_date, 'Contract Ticker')

# eof
