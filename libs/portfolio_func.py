import pandas as pd

def calc_daily_return(df_merge, prev_day_date, aggregation_level):
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

    return dly_pl


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
