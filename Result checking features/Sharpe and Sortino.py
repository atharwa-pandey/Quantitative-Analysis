# -*- coding: utf-8 -*-
"""
Sharpe Ratio 

Created on Thu Aug 11 09:59:14 2022

@author: 91982
"""

import yfinance as yf
import pandas as pd
import numpy as np

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

def volatility(DF):
    df = DF.copy()
    df["return"]=df["Adj Close"].pct_change()
    vol = df["return"].std() * np.sqrt(252)
    return vol

def sharpe(DF,rf=0.03):
    df = DF.copy()
    return (CAGR(df) - rf)/volatility(df)

def sortino(DF,rf=0.03):
    df = DF.copy()
    df["return"] = df["Adj Close"].pct_change()
    neg_return = np.where(df["return"]>0,0,df["return"])
    neg_vol = pd.Series(neg_return[neg_return!=0]).std() * np.sqrt(252)
    return  (CAGR(df)-rf)/neg_vol

for ticker in ohlcv_data:
    print("Sharpe for {} is {} and its Sortino is {}".format(ticker, sharpe(ohlcv_data[ticker]),sortino(ohlcv_data[ticker])))