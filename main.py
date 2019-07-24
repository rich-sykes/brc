

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


    # merge previous day start prices
    prev_day_date_idx = price_data.index[price_data.index.get_loc(prev_day_date, method='pad')]

    df_prev_day = pd.melt(price_data[price_data.index == prev_day_date_idx].reset_index(),
                             id_vars='Date',
                             value_vars=contract_tickers,
                             var_name='Contract Ticker',
                             value_name='Previous Day Price'
                             )
    df_prev_day['Previous Day Date'] = prev_day_date

    df_merge = pd.merge(df_merge, df_prev_day[['Contract Ticker', 'Previous Day Price', 'Previous Day Date']],
                        left_on=['Contract Ticker'],
                        right_on=['Contract Ticker'], how='left')

    # sort by date
    df_merge.set_index('Trade Date', inplace=True)
    df_merge.sort_index(inplace=True)

    # get final price - current trading price or expiry price
    df_merge['Final Price'] = df_merge['Latest Price']
    df_merge['Final Price'][df_merge['Expired'] == 1] = df_merge['Expiry Price'][df_merge['Expired'] == 1]

    # daily calculation
    daily_df = df_merge[['Contract Ticker', 'Contract Description', 'Instrument Description',
                         'Instrument Asset Class',
                         'Expired', 'Contract Expiry', 'Contract Multiplier', 'Traded Amount',
                         'Previous Day Price', 'Final Price']]

    # remove tickers that have expired as no P/L
    daily_df = daily_df[daily_df['Contract Expiry'] > prev_day_date]

    daily_df['Price Change'] = daily_df['Final Price'] - daily_df['Previous Day Price']

    daily_df['P/L'] = daily_df['Price Change'] * \
                      daily_df['Contract Multiplier'] * \
                      daily_df['Traded Amount']

    daily_df['Status'] = ''
    daily_df['Status'][daily_df['Expired'] == 1] = 'Realised'
    daily_df['Status'][daily_df['Expired'] == 0] = 'Unrealised'

    dly_pl = daily_df.groupby(by=[aggregation_level, 'Status'])['P/L'].sum().unstack(1).fillna(value=0)
    dly_pl.columns = dly_pl.columns.get_level_values(0)
    dly_pl = pd.DataFrame(dly_pl.to_records())
    dly_pl['Sum P/L'] = dly_pl.sum(axis=1, skipna=True)


    # month to date calculation
    df_month = df_merge[['Contract Ticker', 'Contract Description', 'Instrument Description',
                         'Instrument Asset Class',
                         'Expired', 'Contract Expiry', 'Contract Multiplier', 'Traded Amount',
                         'Month Start Price', 'Final Price']]

    # remove tickers that have expired as no P/L
    df_month = df_month[df_month['Contract Expiry'] > month_to_date]

    df_month['Price Change'] = df_month['Final Price'] - df_month['Month Start Price']

    df_month['P/L'] = df_month['Price Change'] * \
                      df_month['Contract Multiplier'] * \
                      df_month['Traded Amount']

    df_month['Status'] = ''
    df_month['Status'][df_month['Expired'] == 1] = 'Realised'
    df_month['Status'][df_month['Expired'] == 0] = 'Unrealised'

    mnt_pl = df_month.groupby(by=[aggregation_level, 'Status'])['P/L'].sum().unstack(1).fillna(value=0)
    mnt_pl.columns = mnt_pl.columns.get_level_values(0)
    mnt_pl = pd.DataFrame(mnt_pl.to_records())
    mnt_pl['Sum P/L'] = mnt_pl.sum(axis=1, skipna=True)


    # year to date calculation
    df_year = df_merge[['Contract Ticker', 'Contract Description', 'Instrument Description',
                         'Instrument Asset Class',
                         'Expired', 'Contract Expiry', 'Contract Multiplier', 'Traded Amount',
                         'Start Price', 'Final Price']]

    # remove tickers that have expired as no P/L
    df_year = df_year[df_year['Contract Expiry'] > year_to_date]

    df_year['Price Change'] = df_year['Final Price'] - df_year['Start Price']

    df_year['P/L'] = df_year['Price Change'] * \
                      df_year['Contract Multiplier'] * \
                      df_year['Traded Amount']

    df_year['Status'] = ''
    df_year['Status'][df_year['Expired'] == 1] = 'Realised'
    df_year['Status'][df_year['Expired'] == 0] = 'Unrealised'

    year_pl = df_year.groupby(by=[aggregation_level, 'Status'])['P/L'].sum().unstack(1).fillna(value=0)
    year_pl.columns = year_pl.columns.get_level_values(0)
    year_pl = pd.DataFrame(year_pl.to_records())
    year_pl['Sum P/L'] = year_pl.sum(axis=1, skipna=True)




    # Position held in the portfolio( in contracts)
    contracts_held = df_merge[df_merge['Expired'] == 0][[
        'Contract Ticker', 'Contract Description', 'Traded Amount', 'Instrument Asset Class', 'Contract Expiry']]

    contracts_held['Long/Short'] = 'Long'
    contracts_held['Long/Short'][contracts_held['Traded Amount'] < 0] = 'Short'
    contracts_held = contracts_held.groupby(
        by=['Contract Description', 'Long/Short', 'Contract Expiry'])['Traded Amount'].sum().unstack(1).fillna(value=0)
    contracts_held = pd.DataFrame(contracts_held.to_records())



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
