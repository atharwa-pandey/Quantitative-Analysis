# -*- coding: utf-8 -*-
"""
Bollinger Band Implementation

Created on Tue Aug  9 14:19:49 2022

@author: 91982
"""

import yfinance as yf


tickers = ["MSFT" , "AMZN" , "GOOG" , "ADANIPOWER.NS"]
ohlcv_data = {}

for ticker in tickers:
    temp = yf.download(ticker, period='1mo',interval='5m')
    temp.dropna(how="any", inplace=True)
    ohlcv_data[ticker] = temp

def Boll_Band(DF,n=14):
    df=DF.copy()
    df["MB"] = df["Adj Close"].rolling(n).mean() # We will use Simple Moving Average here
    df["UB"] = df["MB"] + 2*df["Adj Close"].rolling(n).std(ddof=0) # Degree of freedom, sample =1, population ke liye 0
    df["LB"] = df["MB"] - 2*df["Adj Close"].rolling(n).std(ddof=0)
    df["BB_Width"] = df["UB"] - df["LB"]
    return df[["MB","UB","LB","BB_Width"]]

for ticker in ohlcv_data:
    ohlcv_data[ticker][["MB","UB","LB","BB_Width"]] = Boll_Band(ohlcv_data[ticker])
    