

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


# aggregation filter
# aggregation_level = 'Instrument Asset Class'  # 'instrument_asset_class'
# aggregation_level = 'Instrument Description'  # 'instrument'
# aggregation_level = 'Contract Ticker'  # 'contract'


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
    # TODO: if current date isn't in price, select previous
    current_date = pd.to_datetime(reporting_date, format="%d/%m/%Y")

    # get financial reporting dates - month start date
    month_to_date = current_date.replace(day=1)

    # get financial reporting dates - month start date
    year_to_date = current_date.replace(day=1, month=1)


    # filter to date of report
    trade_data = trade_data[trade_data.index <= current_date]
    # trade_data = trade_data[trade_data['Contract Ticker'].isin(contract_tickers)]

    # enrich with contract info
    df = pd.merge(trade_data.reset_index(),
                  contract_data[['Contract Ticker', 'Contract Description', 'Instrument Code', 'Contract Multiplier']],
                  on=['Contract Ticker'])

    # enrich with instrument info
    df = pd.merge(df,
                  instrument_data[[
                      'Instrument Code', 'Instrument Description', 'Instrument Asset Class', 'Instrument Currency']],
                  on=['Instrument Code'])


    contract_tickers = df['Contract Ticker'].unique().tolist()

    # filter to by contracts
    #price_data = price_data[contract_tickers]
    price_data = price_data[price_data.index <= current_date]
    df_p = pd.melt(price_data.reset_index(),
                   id_vars='Date',
                   value_vars=contract_tickers,
                   var_name='Contract Ticker',
                   value_name='Daily Price'
                   )

    # final price
    price_data_final = price_data[contract_tickers][price_data.index == current_date]
    df_pf = pd.melt(price_data_final.reset_index(),
                   id_vars='Date',
                   value_vars=contract_tickers,
                   var_name='Contract Ticker',
                   value_name='Final Price'
                   )

    df_merge = pd.merge(df, df_p,
                        left_on=['Trade Date', 'Contract Ticker'],
                        right_on=['Date', 'Contract Ticker'])

    df_merge = pd.merge(df_merge, df_pf[['Final Price', 'Contract Ticker']],
                        left_on=['Contract Ticker'],
                        right_on=['Contract Ticker'])

    # sort by date
    df_merge.set_index('Date', inplace=True)
    df_merge.sort_index(inplace=True)

    # daily p/l: PriceChange * Multiplier * TradeAmount * IF(SELL, -1, 1)
    df_merge['Daily Price Change'] = df_merge['Daily Price'] - df_merge['Avg Price Traded']
    df_merge['Daily P/L'] = df_merge['Daily Price Change'] * \
                            df_merge['Contract Multiplier'] * \
                            df_merge['Traded Amount']

    # overall p/l
    df_merge['Price Change'] = df_merge['Final Price'] - df_merge['Avg Price Traded']
    df_merge['P/L'] = df_merge['Price Change'] * \
                            df_merge['Contract Multiplier'] * \
                            df_merge['Traded Amount']

    # re-order
    df_merge = df_merge[['Trade Date', 'Contract Ticker', 'Contract Description',
                         'Instrument Code', 'Instrument Description', 'Instrument Asset Class', 'Instrument Currency',
                         'Contract Multiplier', 'Traded Amount', 'Avg Price Traded',
                         'Daily Price', 'Daily Price Change', 'Daily P/L',
                         'Final Price', 'Price Change', 'P/L']]


    #df_overall = df_merge.groupby(by=aggregation_level)[aggregation_level, 'P/L'].sum()

    # Daily P&L
    df_daily = df_merge[df_merge.index >= current_date].groupby(by=aggregation_level)['Contract Ticker', 'P/L'].sum()

    # Month-to-date P&L
    df_month = df_merge[df_merge.index >= month_to_date].groupby(by=aggregation_level)['Contract Ticker', 'P/L'].sum()

    # Year-to-date P&L
    df_year = df_merge[df_merge.index >= year_to_date].groupby(by=aggregation_level)['Contract Ticker', 'P/L'].sum()

    # Position held in the portfolio( in contracts)
    contracts_held = df_merge['Contract Description'].unique().tolist()


    # Valuation sum:  units * current price
    df_merge['Final Value'] = df_merge['Traded Amount'] * df_merge['Final Price']
    df_value = df_merge.groupby(by=aggregation_level)['Final Value'].sum()

    # output data -  dictionary
    output = {}

    # Daily P&L
    output['daily'] = df_daily

    # Month-to-date P&L
    output['month'] = df_month

    # Year-to-date P&L
    output['year'] = df_year

    # Valuation
    output['value'] = df_value

    # Position held in the portfolio (in contracts)
    output['contracts'] = contracts_held

    return output


# output = agg_contracts(reporting_date='28/02/2019', aggregation_level='Instrument Asset Class')
# output = agg_contracts(current_date, 'Instrument Description')
# output = agg_contracts(current_date, 'Contract Ticker')

# eof
