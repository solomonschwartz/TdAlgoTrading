import time
import atexit
import datetime
import pprint
import tda

from TdAlgoTrading import get_hist_data, config

API_KEY = config.CONSUMER_KEY
REDIRECT_URI = config.REDIRECT_URI
TOKEN_PATH = config.JSON_PATH
ACCT_NUM = config.ACCOUNT_NUMBER

from symbols import leverage

def make_webdriver():
    # Import selenium here because it's slow to import
    from selenium import webdriver

    driver = webdriver.Chrome()
    atexit.register(lambda: driver.quit())
    return driver


def percent_return(long_short,buy_price,sell_price):
    if long_short == 'L':
        return (sell_price-buy_price)/buy_price
    elif long_short == 'S':
        return (buy_price - sell_price) / buy_price
    else:
        return 0


async def main():
    # Create a new client
    client = tda.auth.easy_client(
        API_KEY,
        REDIRECT_URI,
        TOKEN_PATH,
        make_webdriver, asyncio=True)

    money = 1000
    daily_money = 0
    daily_investment = 0
    prev_closes = {}
    prev_close_time = -1
    for symbol in leverage.keys():
        data = get_hist_data.get_minute_data(symbol)
        if data.size == 0:
            continue
        prev_closes[symbol] = data.iloc[-1][4]
        prev_close_time = data.iloc[-1][0]

    print("Previous close time: ", prev_close_time)
    pprint.pprint(prev_closes)

    # pprint.pprint(prev_closes)
    long_symbols = []
    short_symbols = []
    now = datetime.datetime.now()
    today_time = now.replace(hour=15,minute=45,second=0)
    while now < today_time:
        time.sleep(3)
        now = datetime.datetime.now()

    for symbol in leverage.keys():
        r = await client.get_quote(symbol)
        data = r.json()
        if prev_closes.get(symbol) is None:
            continue

        if data is None:
            continue
        if not data:
            continue
        long_short = 'N'
        try:
            current = data[symbol]['lastPrice']
            previous = prev_closes.get(symbol)

            v_long = 1 + (0.0166 * leverage.get(symbol))
            long = 1 + (0.0066 * leverage.get(symbol))
            v_short = 1 - (0.0166 * leverage.get(symbol))
            short = 1 - (0.0066 * leverage.get(symbol))
            if current >= v_long * previous:
                long_short = 'VL'
                print(symbol, "Long. Price: ", current, ". Prev Close: ", previous)
                order = tda.orders.equities.equity_buy_limit(symbol, 1, current)
                r = await client.place_order(ACCT_NUM, order)
                long_symbols.append(symbol)
            elif current >= long * previous:
                long_short = 'L'
                print(symbol, "Long. Price: ", current, ". Prev Close: ", previous)
                order = tda.orders.equities.equity_buy_limit(symbol, 1, current)
                r = await client.place_order(ACCT_NUM, order)
                long_symbols.append(symbol)
            elif current <= v_short * previous:
                long_short = 'VS'
                print(symbol, "Short. Price: ", current, ". Prev Close: ", previous)
                order = tda.orders.equities.equity_sell_short_limit(symbol, 1, current)
                r = await client.place_order(ACCT_NUM, order)
                short_symbols.append(symbol)
            elif current <= short * previous:
                long_short = 'S'
                print(symbol, "Short. Price: ", current, ". Prev Close: ", previous)
                order = tda.orders.equities.equity_sell_short_limit(symbol, 1, current)
                r = await client.place_order(ACCT_NUM, order)
                short_symbols.append(symbol)
            else:
                print(symbol, "NO TRADE. Price: ", current, ". Prev Close: ", previous)
            # assert r.status_code == httpx.codes.OK, r.raise_for_status()
        except KeyError:
            print(KeyError,symbol)
            continue

    # at end of day sell positions
    now = datetime.datetime.now()
    close_time = now.replace(hour=15,minute=59,second=15)
    while now < close_time:
        time.sleep(3)
        now = datetime.datetime.now()

    for symbol in short_symbols:
        order = tda.orders.equities.equity_buy_to_cover_market(symbol, 1)
        r = await client.place_order(ACCT_NUM, order)
        # assert r.status_code == httpx.codes.OK, r.raise_for_status()
    for symbol in long_symbols:
        order = tda.orders.equities.equity_sell_market(symbol, 1)
        r = await client.place_order(ACCT_NUM, order)
        # assert r.status_code == httpx.codes.OK, r.raise_for_status()

    # It is highly recommended to close your asynchronous client when you are
    # done with it. This step isn't strictly necessary, however not doing so
    # will result in warnings from the async HTTP library.
    await client.close_async_session()


if __name__ == '__main__':
    import asyncio

    asyncio.run(main())