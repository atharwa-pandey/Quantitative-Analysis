# -*- coding: utf-8 -*-
"""
CAGR Implementation

Created on Wed Aug 10 22:05:55 2022

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

for ticker in ohlcv_data:
    print("CAGR for {} = {}".format(ticker, CAGR(ohlcv_data[ticker])))