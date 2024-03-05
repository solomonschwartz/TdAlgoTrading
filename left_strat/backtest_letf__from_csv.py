from symbols import leverage

import atexit
import datetime
import pprint
import pandas as pd
import tda

from TdAlgoTrading import config

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



def load_csv_data(symbols):
    my_columns = ['Symbol','Time', 'Open', 'High', 'Low', 'Close', 'Volume']
    total_data = pd.DataFrame(columns=my_columns)
    for symbol in symbols:
        try:
            data = pd.read_csv(f'../data/{symbol}.csv')
        except FileNotFoundError:
            print(f"NO INFO for {symbol} yet.")
            continue
        try:
            for index, row in data.iterrows():
                close = row['close']
                high = row['high']
                low = row['low']
                open = row['open']
                volume = row['volume']
                time = row['timestamp']
                timestamp = datetime.datetime.strptime(time,"%Y-%m-%d %H:%M:%S")
                hour = timestamp.time().hour
                minute = timestamp.time().minute
                if (not(hour == 15 and minute == 59)) and (not(hour == 15 and minute == 45)):
                    continue
                row = pd.Series([symbol,
                                 timestamp,
                                 open,
                                 high,
                                 low,
                                 close,
                                 volume],
                                index=my_columns)
                total_data = pd.concat([total_data, pd.DataFrame([row])], ignore_index=True)
        except KeyError:
            print("Bad Request")
            pprint.pprint(data)
            return None
    return total_data


def find_candle(data,_symbol,start_date,end_date,_hour,_minute):
    my_columns = ['Symbol','Time', 'Open', 'High', 'Low', 'Close', 'Volume']
    total_data = pd.DataFrame(columns=my_columns)
    try:
        for index, row in data.iterrows():
            symbol = row['Symbol']
            if symbol != _symbol:
                continue
            row_time = row['Time']
            hour = row_time.time().hour
            minute = row_time.time().minute
            date = pd.to_datetime(row_time)
            if not (hour == _hour and minute == _minute):
                continue
            if date.date() < start_date.date():
                continue
            if date.date() > end_date.date():
                continue
            close = row['Close']
            high = row['High']
            low = row['Low']
            open = row['Open']
            volume = row['Volume']
            row = pd.Series([symbol,
                             row_time,
                             open,
                             high,
                             low,
                             close,
                             volume],
                            index=my_columns)
            total_data = pd.concat([total_data, pd.DataFrame([row])], ignore_index=True)
    except KeyError:
        print("Bad Request")
        pprint.pprint(data)
        return None
    return total_data


def is_off_day(date):
    if date.weekday() == 5 or date.weekday() == 6:
        print("_____________________")
        print("OFF DAY")
        print("_____________________")
        return True
    else:
        return False


async def main():
    money = 1000
    money_columns = ['Date', 'Money (EOD)']
    my_columns = ['Symbol', 'Trade Date', 'Percent Change','Long/Short', 'Buy Price', 'Sell Price', 'Success', 'Money Made']
    df = pd.DataFrame(columns=my_columns)
    money_df = pd.DataFrame(columns=money_columns)
    date = datetime.datetime(year=2023,day=1,month=6)
    data = load_csv_data(leverage.keys())

    for i in range(213):
        if date > datetime.datetime.today():
            break
        elif is_off_day(date):
            date += datetime.timedelta(days=1)
            continue

        prev_closes = {}
        prev_close_price = -1
        prev_close_time = -1
        for symbol in leverage.keys():
            # data = get_hist_data.get_close(symbol,start_date=date-datetime.timedelta(days=1),end_date=date-datetime.timedelta(days=1))
            prev_close = find_candle(data=data, _symbol=symbol, start_date=date-datetime.timedelta(days=3),end_date=date-datetime.timedelta(days=1), _hour=15, _minute=59)
            if prev_close is None:
                continue
            if prev_close.size == 0:
                continue
            prev_closes[symbol] = prev_close.iloc[-1]['Close']
            prev_close_time = prev_close.iloc[-1]['Time']
            prev_close_price = prev_close.iloc[-1]['Close']
        # prev = datetime.datetime.fromtimestamp(prev_close_time)
        print("Previous close time: ", prev_close_time)
        print("Previous close price: ", prev_close_price)
        pprint.pprint(prev_closes)
        daily_money = 0
        daily_investment = 0
        for symbol in leverage.keys():
            # r = await client.get_quote(symbol)
            # data = r.json()
            if prev_closes.get(symbol) is None:
                continue

            current_data = find_candle(data=data,_symbol=symbol,start_date=date,end_date=date, _hour=15, _minute=45)
            if current_data is None:
                continue
            if current_data.size==0:
                continue
            long_short = 'N'
            try:
                # current = data[symbol]['lastPrice']
                previous = prev_closes.get(symbol)
                current = current_data.iloc[-1]['Close']
                print("Current Time: ", current_data.iloc[-1]['Time'])
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

            result_data = find_candle(data=data,_symbol=symbol, start_date=date, end_date=date, _hour=15, _minute=59)
            if result_data is None:
                continue
            if result_data.size==0:
                continue
            result_close = result_data.iloc[-1]['Close']
            print("Result Time: ", result_data.iloc[-1]['Time'])
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

        money += daily_money
        m_row = pd.Series([date, money], index=money_columns)
        money_df = pd.concat([money_df,pd.DataFrame([m_row])],ignore_index=True)
        date += datetime.timedelta(days=1)
        df.to_csv('letf_csv_backtest.csv', sep=',', encoding='utf-8')
        money_df.to_csv('letf_csv_backtest_money.csv', sep=',', encoding='utf-8')
        print("Date: ", date, ". Money: ", money)

    print("Money: " , money)


    # It is highly recommended to close your asynchronous client when you are
    # done with it. This step isn't strictly necessary, however not doing so
    # will result in warnings from the async HTTP library.
    await client.close_async_session()


if __name__ == '__main__':
    import asyncio

    asyncio.run(main())