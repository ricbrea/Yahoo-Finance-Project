import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import pandas_datareader as web
import datetime
from decimal import Decimal


# Load the S&P 500 companies ticker symbols
symbols = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0] 
#symbols = symbols.Symbol.to_list()
#symbols = [i.replace('.','-') for i in symbols]
#symbols_pd = pd.DataFrame(symbols, columns= ['Stock Ticker Symbol'])

full_name = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]    
full_name['Symbol'] = full_name['Symbol'].str.replace('.','-')
full_name = full_name.loc[:,['Symbol', 'Security']]   
both_names = pd.DataFrame()
both_names = full_name['Symbol'] + " AKA " + full_name['Security']


# Custom Indicators and Methods
def RSIcalculation(ticker, startDate):
    df = yf.download(tickers=ticker, start=startDate)
    df['MA200'] = df['Adj Close'].rolling(window=200).mean()
    df['price change'] = df['Adj Close'].pct_change()
    df['Positive Trend'] = df['price change'].apply(lambda x: x if x > 0 else 0)
    df['Negative Trend'] = df['price change'].apply(lambda x: x if x < 0 else 0)
    df['Avg Up'] = df['Positive Trend'].ewm(span=19).mean()
    df['Avg Down'] = df['Negative Trend'].ewm(span=19).mean()
    df = df.dropna()
    df['RS'] = df['Avg Up'] / df['Avg Down']
    df['RSI'] = df['RS'].apply(lambda x: 100.0 - (100.0 / (x +1)))
    df.loc[(df['Adj Close'] > df['MA200']) & (df['RSI'] < 30), 'Buy'] = 'Yes'
    df.loc[(df['Adj Close'] < df['MA200']) | (df['RSI'] > 30), 'Buy'] = 'No'
    return df

def getRSISignals(df, days):
    Buying_dates = []
    Selling_dates = []

    for i in range(len(df)-days):
        if 'Yes' in df['Buy'].iloc[i]:
            Buying_dates.append(df.iloc[i+1].name)
            for j in range(1,days):
                if df['RSI'].iloc[i+j] > 69:
                    Selling_dates.append(df.iloc[i+j+1].name)
                    break
                elif j == days-1:
                    Selling_dates.append(df.iloc[i+j+1].name)

    return Buying_dates,Selling_dates

def RSIBacktesting(dfAsset,days):
    buy,sell = getRSISignals(dfAsset,days)
    Profits = (dfAsset.loc[sell].Open.values - dfAsset.loc[buy].Open.values) / dfAsset.loc[buy].Open.values
    wins = [i for i in Profits if i>0]
    winning_rate = (len(wins)/len(Profits) ) * 100.0
    winning_rate = Decimal(str(winning_rate))
    winning_rate = round(winning_rate, 2)
    st.write('The rate at which this RSI strategy is successful is : ' + str(winning_rate) + '%')
    return Profits




st.title("Real Time S&P 500 Stock Data from Yahoo Finance")

st.header("Welcome! This Streamlit App shows S&P 500 data from Yahoo Finance")

stock_choice = st.selectbox("Please select a stock ticker from the S&P 500: ", options=both_names)

start_date = st.date_input("Please choose the start date from which to calculate data from: ", min_value=datetime.datetime(1985, 1, 1), max_value=datetime.date.today())


stock_symbol = stock_choice.split()[0]

if stock_symbol in (item for item in full_name['Symbol'].values.tolist()):
    stock = yf.Ticker(stock_symbol)
    #data = yf.download(stock)
    st.write(stock.history(period='ytd'))
    #this shows YTD timeframe by going to the 1st of the current year up to today
    beginning_of_year = datetime.date(datetime.date.today().year,1,1)
    stock_pandas = web.DataReader(name=stock_symbol, data_source='yahoo', start=beginning_of_year, end = datetime.datetime.now())
    stock_pandas2 = web.DataReader(name=stock_symbol, data_source='yahoo', start=start_date, end = datetime.datetime.now())
    st.dataframe(stock_pandas)
    st.dataframe(stock_pandas2)
#    close = stock_pandas['Adj Close']
#    st.write(close)
#    delta = close.diff(1)
#    delta.dropna(inplace=True)
#    positive = delta.copy()
#    negative = delta.copy()
#    days = 14
#    positive[positive < 0] = 0
#    negative[negative > 0] = 0
#    average_gain = positive.rolling(window=days).mean()
##    average_loss = abs(negative.rolling(window=days).mean())
 #   relative_strength = average_gain / average_loss
#    RSI = 100.0 - (100.0 / (1.0 + relative_strength))
#    combined = pd.DataFrame()
#    combined['Adj Close'] = stock_pandas['Adj Close']
#    combined['RSI'] = RSI 
#    st.write(combined)
    RSIdf = pd.DataFrame()
    RSIdf = RSIcalculation(stock_symbol, start_date)
    st.dataframe(RSIdf)
    RSIdays = st.number_input("Please select the amount of days you want to use for the RSI range.", min_value=2, max_value=365)
    buy_days, sell_days = getRSISignals(RSIdf, RSIdays)
    #Do they want to backtest data?
    backtestOption = st.radio("Do you want to backtest this data? ", options=('Yes' , 'No'))
    if backtestOption == 'Yes':
        st.write("The backtest results: ")
        st.dataframe(RSIBacktesting(RSIdf, RSIdays))
    else:
        st.write("Okay no backtesting!")


else:
    st.write('Ticker does not exist. Try again!')



RSIBacktestingTheWholeSP500 = st.sidebar.button('RSI Backtesting for the whole S&P 500')
if RSIBacktestingTheWholeSP500:
    st.empty()
    matrixsignals = []
    matrixprofits = []

    for i in range(len(full_name['Symbol'].values.tolist())):
            try:
                frame = RSIcalculation(full_name.iloc[i,0], start_date)
                buy,sell = getRSISignals(frame, RSIdays)
                profits = RSIBacktesting(frame, RSIdays)
                matrixsignals.append(buy)
                matrixprofits.append(profits)

                allprofit = []

                for n in matrixprofits:
                    for e in n:
                        allprofit.append(e)
                allWins = [n for n in allprofit if n > 0 ]
                allTimeWinRate = (len(allWins) / len(allprofit)) * 100.0
                allTimeWinRate = Decimal(str(allTimeWinRate))
                allTimeWinRate = round(allTimeWinRate, 2)
                st.write('The all time winning rate under this strategy and parameters for ' + full_name.iloc[i,0] + ' is : ' + str(allTimeWinRate) + '%')

            except ZeroDivisionError:
                st.write('There is no data for this particular company (' + full_name.iloc[i,0] + ') within this timeframe. Sorry.')
