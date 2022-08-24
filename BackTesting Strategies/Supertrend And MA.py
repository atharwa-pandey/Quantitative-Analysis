# -*- coding: utf-8 -*-
"""
SuperTrend Backtesting Strategy

Created on Mon Aug 22 16:24:10 2022

@author: 91982
"""

import numpy as np
import pandas as pd
import yfinance as yf
import datetime as dt
import copy
import statsmodels.api as sm

def ATR(DF,n):
    "function to calculate True Range and Average True Range"
    df = DF.copy()
    df['H-L']=abs(df['High']-df['Low'])
    df['H-PC']=abs(df['High']-df['Close'].shift(1))
    df['L-PC']=abs(df['Low']-df['Close'].shift(1))
    df['TR']=df[['H-L','H-PC','L-PC']].max(axis=1,skipna=False)
    #df['ATR'] = df['TR'].rolling(n).mean()
    df['ATR'] = df['TR'].ewm(span=n,adjust=False,min_periods=n).mean()
    df2 = df.drop(['H-L','H-PC','L-PC'],axis=1)
    return df2['ATR']


def MA(DF,n=200):
    "Function to calculate 200 exponential moving average"
    df=DF.copy()
    df["MA"]=df["Adj Close"].ewm(span=n,min_periods=n).mean()
    df.dropna(inplace=True)
    return df["MA"]

def SuperTrend(DF,multiplier=3,atr_period=10):
    "Function to calculate the supertrend indicator"
    df=copy.deepcopy(DF)
    df["ATR"] = ATR(df,atr_period)
    df["hl2"] = (df["High"]+df["Low"])/2
    final_upperband = df["hl2"] + multiplier*df["ATR"]
    final_lowerband = df["hl2"] - multiplier*df["ATR"]
    supertrend = [True] * len(df)
    for i in range(1,len(df)):
        if df["Close"][i] > final_upperband[i-1]:
            supertrend[i]= True
        elif df["Close"][i] < final_lowerband[i-1]:
            supertrend[i] = False
        else :
            supertrend[i] = supertrend[i-1]   
            # adjustment to the final bands
            if supertrend[i] == True and final_lowerband[i] < final_lowerband[i-1]:
                final_lowerband[i] = final_lowerband[i-1]
            if supertrend[i] == False and final_upperband[i] > final_upperband[i-1]:
                final_upperband[i] = final_upperband[i-1]
    return (supertrend,final_upperband,final_lowerband)
    


def slope(ser,n):
    "function to calculate the slope of n consecutive points on a plot"
    slopes = [i*0 for i in range(n-1)]
    for i in range(n,len(ser)+1):
        y = ser[i-n:i]
        x = np.array(range(n))
        y_scaled = (y - y.min())/(y.max() - y.min())
        x_scaled = (x - x.min())/(x.max() - x.min())
        x_scaled = sm.add_constant(x_scaled)
        model = sm.OLS(y_scaled,x_scaled)
        results = model.fit()
        slopes.append(results.params[-1])
    slope_angle = (np.rad2deg(np.arctan(np.array(slopes))))
    return np.array(slope_angle)


def CAGR(DF):
    "function to calculate the Cumulative Annual Growth Rate of a trading strategy"
    df = DF.copy()
    df["cum_return"] = (1 + df["ret"]).cumprod()
    n = len(df)/(252*78)
    CAGR = (df["cum_return"].tolist()[-1])**(1/n) - 1
    return CAGR

def volatility(DF):
    "function to calculate annualized volatility of a trading strategy"
    df = DF.copy()
    vol = df["ret"].std() * np.sqrt(252*78)
    return vol

def sharpe(DF,rf):
    "function to calculate sharpe ratio ; rf is the risk free rate"
    df = DF.copy()
    sr = (CAGR(df) - rf)/volatility(df)
    return sr
    

def max_dd(DF):
    "function to calculate max drawdown"
    df = DF.copy()
    df["cum_return"] = (1 + df["ret"]).cumprod()
    df["cum_roll_max"] = df["cum_return"].cummax()
    df["drawdown"] = df["cum_roll_max"] - df["cum_return"]
    df["drawdown_pct"] = df["drawdown"]/df["cum_roll_max"]
    max_dd = df["drawdown_pct"].max()
    return max_dd

# Download historical data for selected stocks

#tickers = ["ADANIPOWER.NS"]

tickers = ["MARUTI.NS","TATASTEEL.NS","TECHM.NS","COALINDIA.NS","RELIANCE.NS","BAJAJ-AUTO.NS"
          ,"HEROMOTOCO.NS","BAJAJFINSV.NS","HINDALCO.NS","ICICIBANK.NS","BRITANNIA.NS"
           ,"NTPC.NS","HDFCLIFE.NS","BAJFINANCE.NS","TITAN.NS","TCS.NS","CIPLA.NS",
           "NESTLEIND.NS","APOLLOHOSP.NS","SHREECEM.NS","ITC.NS","BHARTIARTL.NS","ULTRACEMCO.NS",
           "INDUSINDBK.NS","TATACONSUM.NS","LT.NS","WIPRO.NS","ONGC.NS","KOTAKBANK.NS","ADANIPOWER.NS"]
         


ohlc_intraday = {} # directory with ohlc value for each stock   
start = dt.datetime.today()-dt.timedelta(30)
end = dt.datetime.today()

for ticker in tickers:
    ohlc_intraday[ticker] = yf.download(ticker,start,end,interval='5m')
    ohlc_intraday[ticker].dropna(inplace=True,how="all")

# tickers = ohlc_intraday.keys() # redefine tickers variable after removing any tickers with corrupted data

################################Backtesting####################################

ohlc_dict = copy.deepcopy(ohlc_intraday)
tickers_signal = {}
tickers_ret = {}
for ticker in tickers:
    tickers_signal[ticker] = ""
    tickers_ret[ticker] = [0]
    
for ticker in tickers:
    print("calculating MA and SuperTrend for ",ticker)
    
    ohlc_dict[ticker]["ATR"] = ATR(ohlc_dict[ticker],20) #This Atr is for stoploss
    ohlc_dict[ticker]["ma"]= MA(ohlc_dict[ticker])
    ohlc_dict[ticker]["supertrend"] = SuperTrend(ohlc_dict[ticker])[0]
    ohlc_dict[ticker]["final_upperband"] = SuperTrend(ohlc_dict[ticker])[1]
    ohlc_dict[ticker]["final_lowerband"] = SuperTrend(ohlc_dict[ticker])[2]
    ohlc_dict[ticker].dropna(inplace=True)


# identifying signals and calculating daily return (stop loss factored in)
for ticker in tickers:
    print("calculating returns for ",ticker)
    for i in range(1,len(ohlc_dict[ticker])):
        if tickers_signal[ticker] == "":
            tickers_ret[ticker].append(0)
            if ohlc_dict[ticker]["supertrend"][i] == True and ohlc_dict[ticker]["ma"][i]<ohlc_dict[ticker]["Close"][i-1]:
                tickers_signal[ticker] = "Buy"
            elif ohlc_dict[ticker]["supertrend"][i] == False and ohlc_dict[ticker]["ma"][i]>ohlc_dict[ticker]["Close"][i-1]:
                tickers_signal[ticker] = "Sell"
        
        elif tickers_signal[ticker] == "Buy":
            if (ohlc_dict[ticker]["Low"][i]<ohlc_dict[ticker]["Close"][i-1] - ohlc_dict[ticker]["ATR"][i-1]) : ## Trailing StopLoss is met
                tickers_signal[ticker] = ""
                tickers_ret[ticker].append(((ohlc_dict[ticker]["Close"][i-1] - ohlc_dict[ticker]["ATR"][i-1])/ohlc_dict[ticker]["Close"][i-1])-1)
            elif ohlc_dict[ticker]["supertrend"][i] == False and ohlc_dict[ticker]["ma"][i]>ohlc_dict[ticker]["Close"][i-1]:
                tickers_signal[ticker] = "Sell"
                tickers_ret[ticker].append((ohlc_dict[ticker]["Close"][i]/ohlc_dict[ticker]["Close"][i-1])-1)
            else:
                tickers_ret[ticker].append((ohlc_dict[ticker]["Close"][i]/ohlc_dict[ticker]["Close"][i-1])-1)
                
        elif tickers_signal[ticker] == "Sell":
            if ohlc_dict[ticker]["High"][i]>ohlc_dict[ticker]["Close"][i-1] + ohlc_dict[ticker]["ATR"][i-1] : ## Trailing StopLoss is met
                tickers_signal[ticker] = ""
                tickers_ret[ticker].append((ohlc_dict[ticker]["Close"][i-1]/(ohlc_dict[ticker]["Close"][i-1] + ohlc_dict[ticker]["ATR"][i-1]))-1)
            elif ohlc_dict[ticker]["supertrend"][i] == True and ohlc_dict[ticker]["ma"][i]<ohlc_dict[ticker]["Close"][i-1]:
                tickers_signal[ticker] = "Buy"
                tickers_ret[ticker].append((ohlc_dict[ticker]["Close"][i-1]/ohlc_dict[ticker]["Close"][i])-1)
            else:
                tickers_ret[ticker].append((ohlc_dict[ticker]["Close"][i-1]/ohlc_dict[ticker]["Close"][i])-1)
                
    ohlc_dict[ticker]["ret"] = np.array(tickers_ret[ticker])


# calculating overall strategy's KPIs
strategy_df = pd.DataFrame()
for ticker in tickers:
    strategy_df[ticker] = ohlc_dict[ticker]["ret"]
strategy_df["ret"] = strategy_df.mean(axis=1)
CAGR(strategy_df)
sharpe(strategy_df,0.025)
max_dd(strategy_df)  


# vizualization of strategy return
(1+strategy_df["ret"]).cumprod().plot()


#calculating individual stock's KPIs
cagr = {}
sharpe_ratios = {}
max_drawdown = {}
for ticker in tickers:
    print("calculating KPIs for ",ticker)      
    cagr[ticker] =  CAGR(ohlc_dict[ticker])
    sharpe_ratios[ticker] =  sharpe(ohlc_dict[ticker],0.025)
    max_drawdown[ticker] =  max_dd(ohlc_dict[ticker])

KPI_df = pd.DataFrame([cagr,sharpe_ratios,max_drawdown],index=["Return","Sharpe Ratio","Max Drawdown"])      
KPI_df.T
