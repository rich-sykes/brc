"""
collection of aggregation functions

"""

import pandas as pd


# daily p/l
def calc_daily_return(df):

    # daily calculation
    daily_df = df[['Contract Ticker', 'Contract Description',
                   'Instrument Code', 'Instrument Asset Class', 'Instrument Description',
                   'Contract Multiplier', 'Contract Expiry',
                   'Trade Date',
                   'Traded Amount', 'Price', 'Avg Price Traded', 'Expired']]

    # non traded days = 0
    daily_df['Traded Amount'].fillna(0, inplace=True)

    # sort by ticker/date
    daily_df.reset_index().sort_values(['Contract Ticker', 'Date'], inplace=True)

    # cumulative trdaes
    daily_df['Contracts'] = daily_df.groupby(by=['Contract Ticker'])['Traded Amount'].cumsum()
    daily_df.sort_values(['Contract Ticker', 'Date'], inplace=True)

    # contracts as of previous day (sum)
    daily_df['Previous Contracts'] = daily_df.groupby(by=['Contract Ticker'])['Contracts'].shift(periods=1)

    # price change
    daily_df['Price Diff'] = daily_df.groupby(by=['Contract Ticker'])['Price'].diff()

    # PnL for held contracts
    daily_df['PnL Existing'] = daily_df['Previous Contracts'] * daily_df['Price Diff'] * daily_df['Contract Multiplier']

    # PnL for new contracts traded
    daily_df['PnL Traded'] = daily_df['Traded Amount'] * (daily_df['Price'] - daily_df['Avg Price Traded']) * \
        daily_df['Contract Multiplier']

    # PnL daily total
    daily_df['Daily PnL'] = daily_df[['PnL Existing', 'PnL Traded']].sum(axis=1)

    # add realised flag
    daily_df['Status'] = ''
    daily_df['Status'][daily_df['Expired'] == 1] = 'Realised'
    daily_df['Status'][daily_df['Expired'] == 0] = 'Unrealised'

    # valuation
    daily_df['Valuation'] = daily_df[['Traded Amount', 'Previous Contracts']].sum(axis=1) * \
        daily_df['Price'] * daily_df['Contract Multiplier']

    return daily_df


# calculate the valuation on the reporting date
def calc_valuation(daily_df, current_date, aggregation_level):

    daily_df = daily_df[daily_df.index == current_date]
    value_df = daily_df.groupby(by=[aggregation_level])['Valuation'].sum()
    # value_df.columns = value_df.columns.get_level_values(0)

    value_df = pd.DataFrame(value_df).reset_index()
    value_df = value_df[value_df['Valuation'] != 0]

    return value_df


# calculate contracts held on reporting date
def calc_contracts_held(daily_df, current_date):

    daily_df = daily_df[daily_df.index == current_date]
    holding_df = daily_df[['Contract Description', 'Contracts']]
    holding_df.columns = holding_df.columns.get_level_values(0)
    holding_df = holding_df[holding_df['Contracts'] != 0]

    holding_df['Contracts'] = holding_df['Contracts'].astype(int)

    # TODO: split to long/short

    return holding_df


# aggregate the daily returns (aggregation_level)
def calc_daily_aggregate(daily_df, current_date, aggregation_level):

    # filer dates
    daily_df = daily_df[daily_df.index == current_date]

    # if no contracts - remove
    daily_df = daily_df[daily_df['Contracts'] != 0]

    # aggregation
    daily_pnl_df = daily_df.groupby(by=[aggregation_level, 'Status'])['Daily PnL'].sum().unstack(1).fillna(value=0)
    daily_pnl_df.columns = daily_pnl_df.columns.get_level_values(0)
    daily_pnl_df['Sum P/L'] = daily_pnl_df.sum(axis=1, skipna=True)

    daily_pnl_df = pd.DataFrame(daily_pnl_df.to_records())

    return daily_pnl_df


# aggregate the (month to date) returns (aggregation_level)
def calc_mtd_aggregate(daily_df, current_date, aggregation_level):

    # get financial reporting dates - month start date
    month_to_date = current_date.replace(day=1)

    # filter dates
    daily_df = daily_df[daily_df.index <= current_date]
    daily_df = daily_df[daily_df.index >= month_to_date]


    # aggregate
    month_pnl_df = daily_df.groupby(by=[aggregation_level, 'Status'])['Daily PnL'].sum().unstack(1).fillna(value=0)
    # as timeseries
    #daily_df['CumPnL'] = daily_df.groupby(by=[aggregation_level, 'Status'])['Daily PnL'].cumsum()

    month_pnl_df.columns = month_pnl_df.columns.get_level_values(0)
    month_pnl_df['Sum P/L'] = month_pnl_df.sum(axis=1, skipna=True)

    month_pnl_df = pd.DataFrame(month_pnl_df.to_records())

    # TODO: could remove where PnL is zero on a traded contract
    month_pnl_df = month_pnl_df[month_pnl_df['Sum P/L'] != 0]

    return month_pnl_df


# year to date p/l
def calc_ytd_aggregate(daily_df, current_date, aggregation_level):

    # get financial reporting dates - month start date
    year_to_date = current_date.replace(day=1, month=1)

    # filter dates
    daily_df = daily_df[daily_df.index <= current_date]
    daily_df = daily_df[daily_df.index >= year_to_date]

    # aggregate
    year_pnl_df = daily_df.groupby(by=[aggregation_level, 'Status'])['Daily PnL'].sum().unstack(1).fillna(value=0)
    # as timeseries
    #year_pnl_df['CumPnL'] = daily_df.groupby(by=[aggregation_level, 'Status'])['Daily PnL'].cumsum()

    year_pnl_df.columns = year_pnl_df.columns.get_level_values(0)
    year_pnl_df['Sum P/L'] = year_pnl_df.sum(axis=1, skipna=True)

    year_pnl_df = pd.DataFrame(year_pnl_df.to_records())

    # TODO: could remove where PnL is zero on a traded contract
    year_pnl_df = year_pnl_df[year_pnl_df['Sum P/L'] != 0]

    return year_pnl_df