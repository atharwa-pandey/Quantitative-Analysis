# -*- coding: utf-8 -*-
"""
Measuring the volatility of a buy and hold strategy

Created on Wed Aug 10 22:20:44 2022

@author: 91982
"""

import yfinance as yf
import numpy as np


tickers = ["MSFT" , "AMZN" , "GOOG" , "ADANIPOWER.NS"]
ohlcv_data = {}

for ticker in tickers:
    temp = yf.download(ticker, period='7mo',interval='1d')
    temp.dropna(how="any", inplace=True)
    ohlcv_data[ticker] = temp
    
def volatility(DF):
    df = DF.copy()
    df["return"]=df["Adj Close"].pct_change()
    vol = df["return"].std() * np.sqrt(252)
    return vol

for ticker in ohlcv_data:
    print("Volatility for {} is {}".format(ticker, volatility(ohlcv_data[ticker])))