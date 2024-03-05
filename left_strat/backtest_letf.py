from symbols import leverage

import time
import atexit
import datetime
import pprint
import pandas as pd
import tda

from TdAlgoTrading import get_hist_data, config

API_KEY = config.CONSUMER_KEY
REDIRECT_URI = config.REDIRECT_URI
TOKEN_PATH = config.JSON_PATH
ACCT_NUM = config.ACCOUNT_NUMBER

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
    make_webdriver, asyncio=True)


def percent_return(long_short,buy_price,sell_price):
    if long_short == 'L' or long_short == 'VL':
        return (sell_price-buy_price)/buy_price
    elif long_short == 'S' or long_short == 'VS':
        return (buy_price - sell_price) / buy_price
    else:
        return 0


async def main():
    money = 1000
    money_columns = ['Date', 'Money (EOD)']
    my_columns = ['Symbol', 'Trade Date', 'Percent Change','Long/Short', 'Buy Price', 'Sell Price', 'Success', 'Money Made']
    df = pd.DataFrame(columns=my_columns)
    money_df = pd.DataFrame(columns=money_columns)
    date = datetime.datetime(year=2023,day=8,month=12)
    m_row = pd.Series([date, money], index=money_columns)
    money_df = pd.concat([money_df, pd.DataFrame([m_row])], ignore_index=True)
    for i in range(20):
        print("DATE:", date)
        if date > datetime.datetime.today():
            break
        if date.weekday() == 5 or date.weekday() == 6:
            print("_____________________")
            print("OFF DAY")
            print("_____________________")
            date += datetime.timedelta(days=1)
            continue
        prev_closes = {}
        prev_close_time = -1
        for symbol in leverage.keys():
            # data = get_hist_data.get_close(symbol,start_date=date-datetime.timedelta(days=1),end_date=date-datetime.timedelta(days=1))
            data = get_hist_data.get_minute_data(symbol, start_date=date - datetime.timedelta(days=3),
                                                 end_date=date - datetime.timedelta(days=1))
            if data is None:
                continue
            if data.size == 0:
                continue
            prev_closes[symbol] = data.iloc[-1][4]
            prev_close_time = data.iloc[-1][0]
        # prev = datetime.datetime.fromtimestamp(prev_close_time)
        print("Previous close time: ", prev_close_time)
        pprint.pprint(prev_closes)
        daily_money = 0
        daily_investment = 0
        for symbol in leverage.keys():
            # r = await client.get_quote(symbol)
            # data = r.json()
            if prev_closes.get(symbol) is None:
                continue

            data = get_hist_data.get_minute_data(symbol, start_date=date, end_date=date, _hour=15, _minute=45)
            if data is None:
                continue
            if data.size==0:
                continue
            long_short = 'N'
            try:
                # current = data[symbol]['lastPrice']
                previous = prev_closes.get(symbol)
                current = data.iloc[-1][4]
                print("Current Time: ", data.iloc[-1][0])
                v_long = 1 + (0.0166 * leverage.get(symbol))
                long = 1 + (0.0066 * leverage.get(symbol))
                v_short = 1 - (0.0166 * leverage.get(symbol))
                short = 1 - (0.0066 * leverage.get(symbol))
                if current >= v_long * previous:
                    long_short = 'VL'
                elif current >= long*previous:
                    long_short = 'L'
                elif current <= v_short * previous:
                    long_short = 'VS'
                elif current <= short * previous:
                    long_short = 'S'
            except KeyError:
                print(KeyError,symbol)
                continue

            result_data = get_hist_data.get_minute_data(symbol, start_date=date, end_date=date, _hour=15, _minute=59)
            if result_data is None:
                continue
            if result_data.size==0:
                continue
            result_close = result_data.iloc[-1][4]
            print("Result Time: ", result_data.iloc[-1][0])
            percent = (current-previous)/previous * 100
            success = percent_return(long_short,current,result_close)
            if daily_investment >= money:
                investment = 0
            else:
                investment = money/16 if (long_short == "VL" or long_short == "VS") else money/20
                daily_investment+=investment
            money_made = investment*success
            if long_short != 'N':
                row = pd.Series([symbol,date,percent,long_short,current,result_close,success,money_made], index=my_columns)
                df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
            daily_money+=money_made
        time.sleep(20)
        money += daily_money
        m_row = pd.Series([date, money], index=money_columns)
        money_df = pd.concat([money_df,pd.DataFrame([m_row])],ignore_index=True)
        date += datetime.timedelta(days=1)
        df.to_csv('letf_backtest_2.csv', sep=',', encoding='utf-8')
        money_df.to_csv('letf_backtest_money_2.csv', sep=',', encoding='utf-8')
        print("Date: ", date, ". Money: ", money)

    print("Money: " , money)


    # It is highly recommended to close your asynchronous client when you are
    # done with it. This step isn't strictly necessary, however not doing so
    # will result in warnings from the async HTTP library.
    await client.close_async_session()


if __name__ == '__main__':
    import asyncio

    asyncio.run(main())