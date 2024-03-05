# TdAlgoTrading
Algorithmic Trading Suite to work with TD Ameritrade
Capabilities include: backtesting, generating historical data, and live market trading

# Before Use
1. Must update config_example.py to include account information for TD Ameritrade. To get started, see the following:
   1. https://developer.tdameritrade.com/
   2. https://pypi.org/project/td-ameritrade-python-api/
2. Must generate api key from alphavantage. To get started, see:
   1. https://www.alphavantage.co/

# Basic Overview of Code
1. alphaVantage.py is responsible for generating the data to backtest on
2. Data is stored in the TdAlgoTrading/data folder. Each symbol has its own CSV file. Example, the data for the symbol BULZ is stored at TdAlgoTrading/data/BULZ.csv
3. getHistData.py is a helper function used by each strategy to fetch clean data from the correct TdAlgoTrading/data/symbol.csv file.
4. Each Strategy has its own independent folder. I only uploaded a strategy that I do not currently use called letf_strat.
5. Within letf_strat, there are a few important files:
   1. backtest_letf.py is the basic backtesting framework that uses the TD Ameritrade built-in historical data API. 
   2. backtest_letf_from_csv.py is the more advanced backtesting framework that backtests on the data stored in the TdAlgoTrading/data folder. 
   3. live_market_letf.py is responsible for live trading using the letf_strategy 
   4. symbols.py contains the symbols used in backtesting 
   5. strategy_writeup.pdf contains the basic explanation of the strategy

   
