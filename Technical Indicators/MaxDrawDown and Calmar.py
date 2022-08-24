# -*- coding: utf-8 -*-
"""
Max drawdown and Calmar Ratio

Created on Thu Aug 11 10:13:49 2022

@author: 91982
"""

import yfinance as yf


tickers = ["MSFT" , "AMZN" , "GOOG" , "ADANIPOWER.NS"]
ohlcv_data = {}

for ticker in tickers:
    temp = yf.download(ticker, period='7mo',interval='1d')
    temp.dropna(how="any", inplace=True)
    ohlcv_data[ticker] = temp
    
def CAGR(DF):
    df = DF.copy()
    df["return"] = df["Adj Close"].pct_change()
    df["cum_return"] = (1+df["return"]).cumprod()
    n = len(df)/252
    CAGR = (df["cum_return"][-1])**(1/n) - 1
    return CAGR
    
def max_dd(DF):    
    df = DF.copy()
    df["return"] = df["Adj Close"].pct_change()
    df["cum_return"] = (1+df["return"]).cumprod()
    df["cum_roll_max"] = df["cum_return"].cummax()
    df["drawdown"] = df["cum_roll_max"] - df["cum_return"]
    return (df["drawdown"]/df["cum_roll_max"]).max()

def calmar(DF):
    df=DF.copy()
    return CAGR(df)/max_dd(df)

for ticker in ohlcv_data:
    print("Max drawdown of {} is {}".format(ticker, max_dd(ohlcv_data[ticker])))
    print("Calmar Ratio of {} is {}".format(ticker, calmar(ohlcv_data[ticker])))
