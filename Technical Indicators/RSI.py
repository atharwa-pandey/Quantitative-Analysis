# -*- coding: utf-8 -*-
"""
Relative Strength Index (RSI)

Created on Tue Aug  9 19:13:39 2022

@author: 91982
"""

import yfinance as yf
import numpy as np


tickers = ["MSFT" , "AMZN" , "GOOG" , "ADANIPOWER.NS"]
ohlcv_data = {}

for ticker in tickers:
    temp = yf.download(ticker, period='1mo',interval='5m')
    temp.dropna(how="any", inplace=True)
    ohlcv_data[ticker] = temp
    
def RSI(DF,n=14):
    df=DF.copy()
    df["change"] = df["Adj Close"] - df["Adj Close"].shift(1)
    df["gain"] = np.where(df["change"]>=0,df["change"],0)
    df["loss"] = np.where(df["change"]<0,-1*df["change"],0) #If else statement
    df["avgGain"] = df["gain"].ewm(alpha=1/n , min_periods=n).mean()  # rma function, alhpa is 1/n(Smoothing factor)
    df["avgLoss"] = df["loss"].ewm(alpha=1/n , min_periods=n).mean()
    df["rs"] = df["avgGain"]/df["avgLoss"]
    df["rsi"] = 100 - (100/(1+df["rs"]))
    return df["rsi"]

for ticker in ohlcv_data:
    ohlcv_data[ticker]["RSI"] = RSI(ohlcv_data[ticker])