# -*- coding: utf-8 -*-
"""
Created on Fri Aug 19 17:34:16 2022

@author: 91982
"""

# =============================================================================
# Backtesting strategy - V : combining RSI with other MACD

# Please report bug/issues in the Q&A section
# =============================================================================

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
    df['ATR'] = df['TR'].rolling(n).mean()
    #df['ATR'] = df['TR'].ewm(span=n,adjust=False,min_periods=n).mean()
    df2 = df.drop(['H-L','H-PC','L-PC'],axis=1)
    return df2['ATR']

def MACD(DF,a,b,c):
    """function to calculate MACD
       typical values a = 12; b =26, c =9"""
    df = DF.copy()
    df["MA_Fast"]=df["Adj Close"].ewm(span=a,min_periods=a).mean()
    df["MA_Slow"]=df["Adj Close"].ewm(span=b,min_periods=b).mean()
    df["MACD"]=df["MA_Fast"]-df["MA_Slow"]
    df["Signal"]=df["MACD"].ewm(span=c,min_periods=c).mean()
    df.dropna(inplace=True)
    return (df["MACD"],df["Signal"])

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

# Download historical data (monthly) for selected stocks

tickers = ["MARUTI.NS","TATASTEEL.NS","TECHM.NS","COALINDIA.NS","RELIANCE.NS","BAJAJ-AUTO.NS"
           ,"HEROMOTOCO.NS","BAJAJFINSV.NS","HINDALCO.NS","ICICIBANK.NS","BRITANNIA.NS"
           ,"NTPC.NS","HDFCLIFE.NS","BAJFINANCE.NS","TITAN.NS","TCS.NS","CIPLA.NS",
           "NESTLEIND.NS","APOLLOHOSP.NS","SHREECEM.NS","ITC.NS","BHARTIARTL.NS","ULTRACEMCO.NS",
           "INDUSINDBK.NS","TATACONSUM.NS","LT.NS","WIPRO.NS","ONGC.NS","KOTAKBANK.NS"]
         


ohlc_intraday = {} # directory with ohlc value for each stock   
start = dt.datetime.today()-dt.timedelta(30)
end = dt.datetime.today()

for ticker in tickers:
    ohlc_intraday[ticker] = yf.download(ticker,start,end,interval='5m')
    ohlc_intraday[ticker].dropna(inplace=True,how="all")

# tickers = ohlc_intraday.keys() # redefine tickers variable after removing any tickers with corrupted data

################################Backtesting####################################

# calculating ATR and rolling max price for each stock and consolidating this info by stock in a separate dataframe
ohlc_dict = copy.deepcopy(ohlc_intraday)
tickers_signal = {}
tickers_ret = {}
for ticker in tickers:
    tickers_signal[ticker] = ""
    tickers_ret[ticker] = [0]
    
for ticker in tickers:
    print("calculating MACD and RSI for ",ticker)
    
    ohlc_dict[ticker]["ATR"] = ATR(ohlc_dict[ticker],20)
    '''ohlc_dict[ticker]["roll_max_cp"] = ohlc_dict[ticker]["High"].rolling(20).max()
    ohlc_dict[ticker]["roll_min_cp"] = ohlc_dict[ticker]["Low"].rolling(20).min()
    ohlc_dict[ticker]["roll_max_vol"] = ohlc_dict[ticker]["Volume"].rolling(20).max()
    '''
    ohlc_dict[ticker]["macd"]= MACD(ohlc_dict[ticker],12,26,9)[0]
    ohlc_dict[ticker]["macd_sig"]= MACD(ohlc_dict[ticker],12,26,9)[1]
    ohlc_dict[ticker]["macd_slope"] = slope(ohlc_dict[ticker]["macd"],5)
    ohlc_dict[ticker]["macd_sig_slope"] = slope(ohlc_dict[ticker]["macd_sig"],5)
    ohlc_dict[ticker]["RSI"] = RSI(ohlc_dict[ticker],9)
    ohlc_dict[ticker].dropna(inplace=True)


# identifying signals and calculating daily return (stop loss factored in)
for ticker in tickers:
    print("calculating returns for ",ticker)
    for i in range(1,len(ohlc_dict[ticker])):
        if tickers_signal[ticker] == "":
            tickers_ret[ticker].append(0)
            if ohlc_dict[ticker]["RSI"][i]<=45 and ohlc_dict[ticker]["macd"][i]>ohlc_dict[ticker]["macd_sig"][i] and ohlc_dict[ticker]["macd_slope"][i]>ohlc_dict[ticker]["macd_sig_slope"][i]:
                tickers_signal[ticker] = "Buy"
            elif ohlc_dict[ticker]["RSI"][i]>=75 and ohlc_dict[ticker]["macd"][i]<ohlc_dict[ticker]["macd_sig"][i] and ohlc_dict[ticker]["macd_slope"][i]<ohlc_dict[ticker]["macd_sig_slope"][i]:
                tickers_signal[ticker] = "Sell"
        
        elif tickers_signal[ticker] == "Buy":
            if (ohlc_dict[ticker]["Low"][i]<ohlc_dict[ticker]["Close"][i-1] - ohlc_dict[ticker]["ATR"][i-1]) : ## Trailing StopLoss is met
                tickers_signal[ticker] = ""
                tickers_ret[ticker].append(((ohlc_dict[ticker]["Close"][i-1] - ohlc_dict[ticker]["ATR"][i-1])/ohlc_dict[ticker]["Close"][i-1])-1)
          #  elif ohlc_dict[ticker]["Low"][i]<=ohlc_dict[ticker]["roll_min_cp"][i] and \
          #     ohlc_dict[ticker]["Volume"][i]>1.5*ohlc_dict[ticker]["roll_max_vol"][i-1]:
          #      tickers_signal[ticker] = "Sell"
          #      tickers_ret[ticker].append((ohlc_dict[ticker]["Close"][i]/ohlc_dict[ticker]["Close"][i-1])-1)
            else:
                tickers_ret[ticker].append((ohlc_dict[ticker]["Close"][i]/ohlc_dict[ticker]["Close"][i-1])-1)
                
        elif tickers_signal[ticker] == "Sell":
            if ohlc_dict[ticker]["High"][i]>ohlc_dict[ticker]["Close"][i-1] + ohlc_dict[ticker]["ATR"][i-1] : ## Trailing StopLoss is met
                tickers_signal[ticker] = ""
                tickers_ret[ticker].append((ohlc_dict[ticker]["Close"][i-1]/(ohlc_dict[ticker]["Close"][i-1] + ohlc_dict[ticker]["ATR"][i-1]))-1)
          #  elif ohlc_dict[ticker]["High"][i]>=ohlc_dict[ticker]["roll_max_cp"][i] and \
          #     ohlc_dict[ticker]["Volume"][i]>1.5*ohlc_dict[ticker]["roll_max_vol"][i-1]:
          #      tickers_signal[ticker] = "Buy"
          #      tickers_ret[ticker].append((ohlc_dict[ticker]["Close"][i-1]/ohlc_dict[ticker]["Close"][i])-1)
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