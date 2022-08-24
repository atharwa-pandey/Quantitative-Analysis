# -*- coding: utf-8 -*-
"""
ATR Implementation

Created on Tue Aug  9 14:03:42 2022

@author: 91982
"""
import yfinance as yf


tickers = ["MSFT" , "AMZN" , "GOOG" , "ADANIPOWER.NS"]
ohlcv_data = {}

for ticker in tickers:
    temp = yf.download(ticker, period='1mo',interval='5m')
    temp.dropna(how="any", inplace=True)
    ohlcv_data[ticker] = temp

def ATR(DF,n=14):
    df = DF.copy()
    df["H-L"] = df["High"] - df["Low"]
    df["H-PC"] = df["High"] - df["Adj Close"].shift(1)
    df["L-PC"] = df["Low"] - df["Adj Close"].shift(1)
    df["True Range"] = df[["H-L","H-PC","L-PC"]].max(axis=1,skipna=False)
    df["ATR"] = df["True Range"].ewm(com=n, min_periods=n).mean()
    return df["ATR"]

for ticker in ohlcv_data:
    ohlcv_data[ticker]["ATR"] = ATR(ohlcv_data[ticker])