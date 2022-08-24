# -*- coding: utf-8 -*-
"""
Strategy 1 : Monthly Portfolio Rebalancing
BackTesting

Created on Thu Aug 11 12:34:58 2022

@author: 91982
"""
import numpy as np
import pandas as pd
import yfinance as yf
import datetime as dt
import copy
import matplotlib.pyplot as plt

def CAGR(DF):
    "This is a function to calculate the Cummulative Annual Growth Rate of Strategy"
    df = DF.copy()
    df["cum_return"] = (1+df["mon_ret"]).cumprod()
    n = len(df)/12
    CAGR = (df["cum_return"].tolist()[-1])**(1/n) - 1
    return CAGR

def volatility(DF):
    "Function to calculate annualized volatility of a trading strategy"
    df = DF.copy()
    vol = df["mon_ret"].std() * np.sqrt(12)
    return vol

def sharpe(DF,rf):
    "Function to calculate the sharpe ratio of the strategy, rf is the risk free rate"
    df = DF.copy()
    sr = (CAGR(df)-rf)/volatility(df)
    return sr

def max_dd(DF):
    "Function to calculate max drawdown"
    df = DF.copy()
    df["cum_return"] = (1 + df["mon_ret"]).cumprod()
    df["cum_roll_max"] = df["cum_return"].cummax()
    df["drawdown"] = df["cum_roll_max"] - df["cum_return"]
    df["drawdown_pct"] = df["drawdown"]/df["cum_roll_max"]
    max_dd = df["drawdown_pct"].max()
    return max_dd

#These are the stocks that we will take into our account 

tickers = ["HEROMOTOCO.NS","BRITANNIA.NS","ULTRACEMCO.NS","NESTLEIND.NS",
           "BAJAJ-AUTO.NS","HDFCLIFE.NS","COALINDIA.NS","TATASTEEL.NS","CIPLA.NS",
           "RELIANCE.NS","ONGC.NS","SHREECEM.NS","BHARTIARTL.NS","BAJAJFINSV.NS","LT.NS"
           ,"HINDALCO.NS","ICICIBANK.NS","NTPC.NS","KOTAKBANK.NS","MARUTI.NS","ITC.NS","TITAN.NS"
           ,"APOLLOHOSP.NS","INDUSINDBK.NS","BAJFINANCE.NS","TCS.NS","TATACONSUM.NS"
           ,"WIPRO.NS","TECHM.NS"]

ohlc_mon = {} # directory with ohlc value for each stock            
start = dt.datetime.today()-dt.timedelta(1825)
end = dt.datetime.today()

# looping over tickers and creating a dataframe with close prices
for ticker in tickers:
    ohlc_mon[ticker] = yf.download(ticker,start,end,interval='1mo')
    ohlc_mon[ticker].dropna(inplace=True,how="all")
 
tickers = ohlc_mon.keys() # redefine tickers variable after removing any tickers with corrupted data

################################Backtesting####################################

# calculating monthly return for each stock and consolidating return info by stock in a separate dataframe
ohlc_dict = copy.deepcopy(ohlc_mon)
return_df = pd.DataFrame()
for ticker in tickers:
    print("calculating monthly return for ",ticker)
    ohlc_dict[ticker]["mon_ret"] = ohlc_dict[ticker]["Adj Close"].pct_change()
    return_df[ticker] = ohlc_dict[ticker]["mon_ret"]
return_df.dropna(inplace=True)

# function to calculate portfolio return iteratively
def pflio(DF,m,x):
    """Returns cumulative portfolio return
    DF = dataframe with monthly return info for all stocks
    m = number of stock in the portfolio
    x = number of underperforming stocks to be removed from portfolio monthly"""
    df = DF.copy()
    portfolio = []
    monthly_ret = [0]
    for i in range(len(df)):
        if len(portfolio) > 0:
            monthly_ret.append(df[portfolio].iloc[i,:].mean())
            bad_stocks = df[portfolio].iloc[i,:].sort_values(ascending=True)[:x].index.values.tolist()
            portfolio = [t for t in portfolio if t not in bad_stocks]
        fill = m - len(portfolio)
        new_picks = df.iloc[i,:].sort_values(ascending=False)[:fill].index.values.tolist()
        portfolio = portfolio + new_picks
        #print(portfolio)
    monthly_ret_df = pd.DataFrame(np.array(monthly_ret),columns=["mon_ret"])
    return monthly_ret_df


#calculating overall strategy's KPIs
CAGR(pflio(return_df,7,3))
sharpe(pflio(return_df,7,3),0.074)
max_dd(pflio(return_df,7,3)) 

#calculating KPIs for Index buy and hold strategy over the same period
BSESN = yf.download("^BSESN",dt.date.today()-dt.timedelta(1825),dt.date.today(),interval='1mo')
BSESN["mon_ret"] = BSESN["Adj Close"].pct_change().fillna(0)
CAGR(BSESN)
sharpe(BSESN,0.074)
max_dd(BSESN)

#visualization
fig, ax = plt.subplots()
plt.plot((1+pflio(return_df,7,3)).cumprod())
plt.plot((1+BSESN["mon_ret"].reset_index(drop=True)).cumprod())
plt.title("Index Return vs Strategy Return")
plt.ylabel("cumulative return")
plt.xlabel("months")
ax.legend(["Strategy Return","Index Return"])



