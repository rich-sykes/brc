"""
collection of aggregation functions

"""

import pandas as pd


# daily p/l
def calc_daily_return(df, current_date, prev_day_date, aggregation_level):

    # daily calculation
    daily_df = df[['Contract Ticker', 'Contract Description', 'Instrument Code',
                   'Contract Multiplier', 'Contract Expiry',
                   'Trade Date',
                   'Traded Amount', 'Price', 'Avg Price Traded', 'Expired']]

    # remove tickers that have expired as no P/L
    # daily_df = daily_df[daily_df['Expired'] == 0]

    # Contracts as of yesterday
    daily_df['Traded Amount'].fillna(0, inplace=True)
    daily_df.reset_index().sort_values(['Contract Ticker', 'Date'], inplace=True)

    daily_df['Contracts'] = daily_df.groupby(by=['Contract Ticker'])['Traded Amount'].cumsum()
    daily_df.sort_values(['Contract Ticker', 'Date'], inplace=True)

    # previous contracts (sum)
    daily_df['Previous Contracts'] = daily_df.groupby(by=['Contract Ticker'])['Contracts'].shift(periods=1)

    # price change
    daily_df['Price Diff'] = daily_df.groupby(by=['Contract Ticker'])['Price'].diff()

    # PnL for held contracts
    daily_df['PnL Existing'] = daily_df['Previous Contracts'] * daily_df['Price Diff'] * daily_df['Contract Multiplier']

    # PnL for contracts traded
    daily_df['PnL Traded'] = daily_df['Traded Amount'] * (daily_df['Price'] - daily_df['Avg Price Traded']) * daily_df['Contract Multiplier']

    # PnL total
    daily_df['Daily PnL'] = daily_df['PnL Existing'] + daily_df['PnL Traded']
    daily_df['Daily PnL'] = daily_df[['PnL Existing', 'PnL Traded']].sum(axis=1)

    # add realised flag
    daily_df['Status'] = ''
    daily_df['Status'][daily_df['Expired'] == 1] = 'Realised'
    daily_df['Status'][daily_df['Expired'] == 0] = 'Unrealised'

    daily_df = daily_df[daily_df.index == current_date]

    # valuation
    daily_df['Valuation'] = daily_df[['Traded Amount', 'Previous Contracts']].sum(axis=1) * daily_df['Price'] * daily_df['Contract Multiplier']




    dly_pl = daily_df.groupby(by=[aggregation_level, 'Status'])['P/L'].sum().unstack(1).fillna(value=0)
    dly_pl.columns = dly_pl.columns.get_level_values(0)
    dly_pl = pd.DataFrame(dly_pl.to_records())
    dly_pl['Sum P/L'] = dly_pl.sum(axis=1, skipna=True)

    return dly_pl


# month to date p/l
def calc_mtd_return(df_merge, month_to_date, aggregation_level):

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

    return mnt_pl


# year to date p/l
def calc_ytd_return(df_merge, year_to_date, aggregation_level):

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

    return year_pl


# get all contracts held
def calc_contracts_held(df_merge):

    # Position held in the portfolio( in contracts)
    contracts_held = df_merge[df_merge['Expired'] == 0][[
        'Contract Ticker', 'Contract Description', 'Traded Amount', 'Instrument Asset Class', 'Contract Expiry']]

    contracts_held['Long/Short'] = 'Long'
    contracts_held['Long/Short'][contracts_held['Traded Amount'] < 0] = 'Short'
    contracts_held = contracts_held.groupby(
        by=['Contract Description', 'Long/Short', 'Contract Expiry'])['Traded Amount'].sum().unstack(1).fillna(value=0)
    contracts_held = pd.DataFrame(contracts_held.to_records())

    contracts_held.Long = contracts_held.Long.astype(str)
    contracts_held.Short = contracts_held.Short.astype(str)

    return contracts_held
