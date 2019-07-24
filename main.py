

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
from libs.portfolio_func import calc_daily_return, calc_mtd_return, calc_ytd_return, calc_contracts_held


# aggregation filter
# aggregation_level = 'Instrument Asset Class'
# aggregation_level = 'Instrument Description'
# aggregation_level = 'Contract Ticker'


def agg_contracts(reporting_date, aggregation_level):

    # reporting_date = '17/06/2019' reporting_date = '07/06/2019'
    # aggregation_level = 'Instrument Asset Class'

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

    # get financial reporting dates - previous day
    prev_day_date = current_date - pd.Timedelta(days=1)

    # get financial reporting dates - month start date
    month_to_date = current_date.replace(day=1)

    # get financial reporting dates - month start date
    year_to_date = current_date.replace(day=1, month=1)


    # filter to date of report (remnove future trades)
    trade_data = trade_data[trade_data.index <= current_date]

    # enrich with contract info
    df = pd.merge(trade_data.reset_index(),
                  contract_data[['Contract Ticker', 'Contract Description', 'Instrument Code',
                                 'Contract Multiplier', 'Contract Expiry']],
                  on=['Contract Ticker'])

    # contract expired flag
    df['Expired'] = 0
    df['Expired'][current_date >= df['Contract Expiry']] = 1


    # enrich with instrument info
    df = pd.merge(df,
                  instrument_data[[
                      'Instrument Code', 'Instrument Description', 'Instrument Asset Class', 'Instrument Currency']],
                  on=['Instrument Code'])

    # get ticker list
    contract_tickers = df['Contract Ticker'].unique().tolist()


    ## price data
    # start price (year to date) - in this case first data point in series
    year_to_date_idx = price_data.index[price_data.index.get_loc(year_to_date, method='backfill')]

    df_price_start = pd.melt(price_data[price_data.index == year_to_date_idx].reset_index(),
                              id_vars='Date',
                              value_vars=contract_tickers,
                              var_name='Contract Ticker',
                              value_name='Start Price'
                              )
    df_price_start['Year to Date'] = df_price_start['Date']

    df_merge = pd.merge(df, df_price_start[['Year to Date', 'Contract Ticker', 'Start Price']],
                        left_on=['Contract Ticker'],
                        right_on=['Contract Ticker'])

    df_merge['Start Price'][df_merge['Trade Date'] > year_to_date] =\
        df_merge['Avg Price Traded'][df_merge['Trade Date'] > year_to_date]


    # latest prices
    current_date_idx = price_data.index[price_data.index.get_loc(current_date, method='pad')]
    df_price_latest = pd.melt(price_data[price_data.index == current_date_idx].reset_index(),
                               id_vars='Date',
                               value_vars=contract_tickers,
                               var_name='Contract Ticker',
                               value_name='Latest Price'
                               )
    df_price_latest['Reporting Date'] = df_price_latest['Date']

    # add latest price
    df_merge = pd.merge(df_merge, df_price_latest[['Reporting Date', 'Contract Ticker', 'Latest Price']],
                        left_on=['Contract Ticker'],
                        right_on=['Contract Ticker'])

    # add price at expiry
    df_price_expiry = pd.melt(price_data.reset_index(),
                              id_vars='Date',
                              value_vars=contract_tickers,
                              var_name='Contract Ticker',
                              value_name='Expiry Price'
                              )
    df_price_expiry['Expiry Date'] = df_price_expiry['Date']

    # merge expiry prices
    df_merge = pd.merge(df_merge, df_price_expiry[['Contract Ticker', 'Expiry Price', 'Expiry Date']],
                        left_on=['Contract Ticker', 'Contract Expiry'],
                        right_on=['Contract Ticker', 'Expiry Date'], how='left')
    # TODO: exception is date is missing from price

    # merge start of month start prices
    # if date is missing using previous data
    month_to_date_idx = price_data.index[price_data.index.get_loc(month_to_date, method='pad')]

    df_price_month = pd.melt(price_data[price_data.index == month_to_date_idx].reset_index(),
                             id_vars='Date',
                             value_vars=contract_tickers,
                             var_name='Contract Ticker',
                             value_name='Month Start Price'
                             )

    df_price_month['Month To Date'] = month_to_date

    df_merge = pd.merge(df_merge, df_price_month[['Contract Ticker', 'Month Start Price', 'Month To Date']],
                        left_on=['Contract Ticker'],
                        right_on=['Contract Ticker'], how='left')


    # get previous day start prices
    prev_day_date_idx = price_data.index[price_data.index.get_loc(prev_day_date, method='pad')]

    df_prev_day = pd.melt(price_data[price_data.index == prev_day_date_idx].reset_index(),
                             id_vars='Date',
                             value_vars=contract_tickers,
                             var_name='Contract Ticker',
                             value_name='Previous Day Price'
                             )
    df_prev_day['Previous Day Date'] = prev_day_date

    # merge previous day start prices
    df_merge = pd.merge(df_merge, df_prev_day[['Contract Ticker', 'Previous Day Price', 'Previous Day Date']],
                        left_on=['Contract Ticker'],
                        right_on=['Contract Ticker'], how='left')

    # sort by date
    df_merge.set_index('Trade Date', inplace=True)
    df_merge.sort_index(inplace=True)

    # get final price - current trading price or expiry price
    df_merge['Final Price'] = df_merge['Latest Price']
    df_merge['Final Price'][df_merge['Expired'] == 1] = df_merge['Expiry Price'][df_merge['Expired'] == 1]


    # calculate P/L
    dly_pl = calc_daily_return(df_merge, prev_day_date, aggregation_level)
    mnt_pl = calc_mtd_return(df_merge, month_to_date, aggregation_level)
    year_pl = calc_ytd_return(df_merge, year_to_date, aggregation_level)


    # get contracts
    contracts_held = calc_contracts_held(df_merge)


    # Valuation sum:  units * current price
    df_merge['Final Value'] = abs(df_merge['Traded Amount']) * df_merge['Avg Price Traded']
    df_value = df_merge.groupby(by=aggregation_level)['Final Value'].sum()


    # output data -  dictionary
    output = {}

    # Daily P&L
    output['daily'] = dly_pl

    # Month-to-date P&L
    output['month'] = mnt_pl

    # Year-to-date P&L
    output['year'] = year_pl

    # Valuation
    # output['value'] = df_value[['Final Value']]
    output['value'] = df_value

    # Position held in the portfolio (in contracts)
    output['contracts'] = contracts_held

    return output

# output = agg_contracts(reporting_date='02/07/2019', aggregation_level='Instrument Asset Class')
# output = agg_contracts(current_date, 'Instrument Description')
# output = agg_contracts(current_date, 'Contract Ticker')

# eof
