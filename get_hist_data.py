import atexit
import datetime
import pprint

import tda

import pandas as pd
import json

import config
from tda.client import Client

API_KEY = config.CONSUMER_KEY
REDIRECT_URI = config.REDIRECT_URI
TOKEN_PATH = config.JSON_PATH
ACCT_NUM = config.ACCOUNT_NUMBER
SYMBOLS = ['SPY', 'QQQ']

my_columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']


def make_webdriver():
    # Import selenium here because it's slow to import
    from selenium import webdriver

    driver = webdriver.Chrome()
    atexit.register(lambda: driver.quit())
    return driver


# Create a new client
client = tda.auth.easy_client(
    API_KEY,
    REDIRECT_URI,
    TOKEN_PATH,
    make_webdriver)


'''
:return closing data for given :param symbol
'''
def get_close(symbol,start_date=None,end_date=None):
    if start_date or end_date:
        hist_data = client.get_price_history(
            symbol=symbol,
            frequency_type=Client.PriceHistory.FrequencyType.DAILY,
            frequency=Client.PriceHistory.Frequency.DAILY,
            period_type=Client.PriceHistory.PeriodType.MONTH,
            start_datetime=start_date,
            end_datetime=end_date
        )
    else:
        hist_data = client.get_price_history(
            symbol=symbol,
            period_type=Client.PriceHistory.PeriodType.MONTH,
            period=Client.PriceHistory.Period.ONE_MONTH,
            frequency_type=Client.PriceHistory.FrequencyType.DAILY,
            frequency=Client.PriceHistory.Frequency.DAILY
        )
    price_history = json.loads(hist_data.text)
    return price_history['candles'][-1]


'''
:return specific minute data for :param _hour and :param_minute
over set of days beginning with start_date - INCLUSIVE and
ending with end_date - EXCLUSIVE
'''
def get_minute_data(symbol, start_date=None, end_date=None, _hour=15, _minute=59):
    if start_date or end_date:
        hist_data = client.get_price_history(
            symbol=symbol,
            period_type=Client.PriceHistory.PeriodType.DAY,
            frequency_type=Client.PriceHistory.FrequencyType.MINUTE,
            frequency=Client.PriceHistory.Frequency.EVERY_MINUTE,
            start_datetime=start_date,
            end_datetime=end_date
        )
    else:
        hist_data = client.get_price_history(
            symbol=symbol,
            period_type=Client.PriceHistory.PeriodType.DAY,
            period=Client.PriceHistory.Period.ONE_DAY,
            frequency_type=Client.PriceHistory.FrequencyType.MINUTE,
            frequency=Client.PriceHistory.Frequency.EVERY_MINUTE
        )

    price_history = json.loads(hist_data.text)

    df = pd.DataFrame(columns=my_columns)
    try:
        for i in range(len(price_history['candles'])):
            close = price_history['candles'][i]['close']
            high = price_history['candles'][i]['high']
            low = price_history['candles'][i]['low']
            open = price_history['candles'][i]['open']
            volume = price_history['candles'][i]['volume']
            time = price_history['candles'][i]['datetime']
            timestamp = datetime.datetime.fromtimestamp(time / 1000)
            hour = timestamp.time().hour
            minute = timestamp.time().minute
            if not (hour == _hour and minute == _minute):
                continue
            row = pd.Series([timestamp,
                           open,
                           high,
                           low,
                           close,
                           volume],
                          index=my_columns)
            df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    except KeyError:
        print("Bad Request")
        pprint.pprint(price_history)
        return None
    return df
