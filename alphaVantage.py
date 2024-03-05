

import pandas as pd
import requests

from left_strat.symbols import leverage

# sample keys
# key: G1UTTR7FE2GAU3RM
# key: "F86EDOUG066FP16H"
# key: X6AJK1B5H8ISLH62

'''
:param symbol is the symbol to generate data for. Format is all-caps (Ex: AAPL)
:param year is the year to get 1-minute ticker data for
:return the df with the data
'''


def generate_1_year_data(symbol, year):
    key = "X6AJK1B5H8ISLH62"
    full_df = pd.DataFrame()
    for month in range(1, 13):
        m = f"{month:02}"
        date = str(year) + "-" + m
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=1min&month={date}&outputsize=full&apikey={key}&datatype=csv"

        df = pd.read_csv(url)
        df = pd.DataFrame(df)
        df.head(3)
        df = df.iloc[::-1]
        full_df = pd.concat([full_df, df], ignore_index=True)

    return full_df


'''
:param symbols is a list of symbols to get data for
:param start_month INCLUSIVE
:param end_month EXCLUSIVE
:param new : if set to true, wipes existing stored data
:return void. Outputs appended dataframe for each symbol into data/SYMBOL.csv
'''


def generate_monthly_data(symbols, year, start_month, end_month, key, new=False):
    for symbol in symbols:
        old_df = None
        if not new:
            old_df = pd.read_csv(f'data/{symbol}.csv', delimiter=',')
            old_df = old_df.iloc[:, 1:]

        full_df = pd.DataFrame()
        for month in range(start_month, end_month):
            m = f"{month:02}"
            date = str(year) + "-" + m
            url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=1min&month={date}&outputsize=full&apikey={key}&datatype=csv&adjusted=false"

            df = pd.read_csv(url)
            df = pd.DataFrame(df)
            df.head(3)
            df = df.iloc[::-1]
            full_df = pd.concat([full_df, df], ignore_index=True)
            print("Finished : ", symbol)

        full_df = pd.concat([full_df, old_df], ignore_index=True)
        full_df.to_csv(f'data/{symbol}.csv')


api_key = 'X6AJK1B5H8ISLH62'
generate_monthly_data(leverage.keys(), 2023, 5, 6, api_key)
