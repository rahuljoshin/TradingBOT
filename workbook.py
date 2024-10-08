'''
import requests

url = ('https://amazon.in')  # Replace this with the URL you are trying to access
response = requests.get(url)

print(response.text)



from nsetools import Nse
import time
nse = Nse()
info = nse.get_quote('RELIANCE')
i = 1
while i == 1:
print(info)
print("Last Traded Price: ", info["lastPrice"])
time.sleep(5)


from datetime import date
from nsepy import get_history
import nsepy as nse

sbin = nse.get_history(symbol='SBIN',
                       start=date(2023, 1, 1),
                       end=date(2023, 1, 10))


from datetime import date
from nsepy import get_history

# Stock futures (Similarly for index futures, set index = True)
stock_fut = get_history(symbol="SBIN",
                        start=date(2023, 1, 1),
                        end=date(2023, 1, 10),
                        futures=True,
                        expiry_date=date(2023, 1, 29))

print(stock_fut)


from datetime import date
import nseazy as nse
#print(nse.nse_holidays())
#print(nse.nse_eq('sbin'))

#nse.help('show_data')
data_required = {'Info' : True } # LTP : True By Default

data = nse.show_data('L&T',data_required)
#print(type(data))


# get all the data of state bank (SBIN) from 01 Feb 2023 to 10 Feb 2023
#state_bank = get_history(symbol='SBIN', start=date(2023, 2, 1), end=date(2023, 2, 10))

# save the data to a csv file
#state_bank.to_csv("sbin-feb.csv")

# plot the data
#state_bank[['VWAP', 'Turnover']].plot(secondary_y='Turnover')



from nsedt import equity as eq
from datetime import date

start_date = date(2023, 1, 1)
end_date = date(2023, 1, 10)
print(eq.get_price(start_date, end_date, symbol="TCS"))
start_date = "01-05-2023"
end_date = "03-05-2023"
print(eq.get_corpinfo(start_date, end_date, symbol="TCS"))
print(eq.get_event(start_date, end_date))
print(eq.get_event())
print(eq.get_marketstatus())
print(eq.get_marketstatus(response_type="json"))
print(eq.get_companyinfo(symbol="TCS"))
print(eq.get_companyinfo(symbol="TCS", response_type="json"))
print(eq.get_chartdata(symbol="TCS"))
print(eq.get_symbols_list()) #print the list of symbols used by NSE for equities


from nsedt import indices as ind
from datetime import date

start_date = date(2023, 10, 1)
end_date = date(2023, 10, 16)
#print(ind.get_price(start_date=start_date, end_date=end_date, symbol="NIFTY 50"))
#print(ind.get_price(start_date=start_date, end_date=end_date, symbol="NIFTYBANK"))


from nsedt import derivatives as der

date = der.get_future_expdate(symbol="nifty")
print(type(date))
print(len(date))
for d in date:
    assert isinstance(d, object)
    print(d)

from nsedt import derivatives as de

start_date = "01-09-2023"
end_date = "03-09-2023"
# date format "%d-%m-%Y"
print(de.get_vix(start_date, end_date))
print(de.get_option_chain_expdate(symbol="TCS"))
#print(de.get_option_chain(symbol="TCS", strike_price='3300', expiry_date="2023-11-30"))
print(de.get_future_price(symbol="TCS", start_date=start_date, end_date=end_date))
print(de.get_future_expdate(symbol="banknifty"))

'''

# Some NSE basic functions this is available any NSE Object (Technical OR Derivatives)
# searching

'''
search_res = nse.search('Syrma SGS')
print(search_res.get('symbols')[0].get('symbol'))

# Last Traded date
print(nse.get_last_traded_date())

# Last traded Status and Nifty val
print(nse.get_market_status_and_current_val())

# NSE Equity Meta info
print(nse.get_nse_equity_meta_info('SYRMA'))

# NSE turnover data
trade_df = nse.get_nse_turnover()
print(trade_df.head())


listc = nse.get_options_expiry('BANKNIFTY', is_index=True) # List of Expires
for l in listc:
    print(l)
'''

'''
from Derivatives import NSE

nse = NSE()
# Index Options - NIFTY
nifty_50_option_chain = nse.get_raw_option_chain(
    ticker='BANKNIFTY',
    is_index=True
)

import pandas as pd
data = pd.DataFrame(nifty_50_option_chain)

for record in data['records']['data']:
    if record['expiryDate'] == '18-Oct-2023':
        print(record['CE'])

'''

'''
from Technical import NSE
import pandas as pd

nse = NSE()

index_df = nse.get_equities_data_from_index()

ohlc = nse.get_all_indices()
# print(ohlc.keys())

for index, row in ohlc.iterrows():
    # Accessing each row
    if row['index'] == 'NIFTY BANK':
        print(row)
'''

'''
import pandas as pd
from Technical import NSE

nse = NSE()
dict = nse.search("HDFCBANK")
data = pd.DataFrame.from_dict(dict, orient='index')
data = data.transpose()
print(data.columns)
print(data['symbols'])
'''

# nseData = pd.DataFrame(dict)
# print(len(nseData['symbols']))

'''

import yfinance as yf
#bnData = yf.download(tickers='^NSEBANK', interval="1h", period="1d")
df = yf.download(tickers='KOTAKBANK.NS', interval="5m", period="1d")

df['Price'] = (df['High']+df['Low'])/2
df['Price_times_Volume'] = df['Price'] * df['Volume']

# Calculate the cumulative sum of (price * volume) and volume
df['Cumulative_Price_Volume'] = df['Price_times_Volume'].cumsum()
df['Cumulative_Volume'] = df['Volume'].cumsum()
df['VWAP'] = df['Cumulative_Price_Volume'] / df['Cumulative_Volume']

print(df['VWAP'])
'''
'''
import yfinance as yf
import pandas as pd
banknifty_Stocks = ["BANDHANBNK.NS", "RBLBANK.NS", "BANKBARODA.NS", "PNB.NS", "ICICIBANK.NS", "SBIN.NS",
                    "IDFCFIRSTB.NS", "AXISBANK.NS", "INDUSINDBK.NS", "HDFCBANK.NS", "KOTAKBANK.NS", "AUBANK.NS"]


interval = '5m'
period = '1d'
result = pd.DataFrame(columns=['Cumulative_Price_Volume', 'Cumulative_Volume', 'VWAP'])
bnData = yf.download(tickers='^NSEBANK', interval=interval, period=period)


for stock in banknifty_Stocks:
    df = yf.download(tickers=stock, interval=interval, period=period)
    # Calculate the total price multiplied by volume

    df['Price'] = (df['High']+df['Low'])/2
    df['Price_times_Volume'] = df['Price'] * df['Volume']

    # Calculate the cumulative sum of (price * volume) and volume
    df['Cumulative_Price_Volume'] = df['Price_times_Volume'].cumsum()
    df['Cumulative_Volume'] = df['Volume'].cumsum()
    df['VWAP'] = df['Cumulative_Price_Volume'] / df['Cumulative_Volume']
    bnData['Volume'] += df['Volume']

    df['Price'] = (df['High']+df['Low'])/2
    df['Price_times_Volume'] = df['Price'] * df['Volume']

# Calculate the cumulative sum of (price * volume) and volume
bnData['Price'] = (bnData['High']+bnData['Low'])/2
bnData['Price_times_Volume'] = bnData['Price'] * bnData['Volume']
bnData['Cumulative_Price_Volume'] = bnData['Price_times_Volume'].cumsum()
bnData['Cumulative_Volume'] = bnData['Volume'].cumsum()
bnData['VWAP'] = bnData['Cumulative_Price_Volume'] / bnData['Cumulative_Volume']

print(bnData)
    #print(bnData['Volume'])

    #result = result.add({'Cumulative_Price_Volume':  df['Cumulative_Price_Volume'],
     #                       'Cumulative_Volume': df['Cumulative_Volume'], 'VWAP': df['VWAP']})

    #result['Cumulative_Price_Volume'] += df['Cumulative_Price_Volume']
    #result['Cumulative_Volume'] += df['Cumulative_Volume']
print(bnData)
    # Calculate VWAP

    #df['BNVWAP'] = Cumulative_Price_Volume/Cumulative_Volume
    # Print the DataFrame with VWAP
    #print(df)
#print(len(result))
#df = yf.download(tickers='^NSEBANK', interval="5m", period="1d")
'''

'''
from Banknifty import BankniftyCls

bn = BankniftyCls()
# currentData = bn.get_Candle(interval='1m', period='5m', look_back=2, latest=False)
# print(currentData['Close'])


data_today = bn.get_BNData()
# print(data[['VWAP', 'Close', 'Volume']].head(1))

from datetime import date
from datetime import timedelta

end_date = date.today()
backDay = -1
start_date = end_date - timedelta(-backDay)

dataYDay = bn.get_BNData(start=start_date, end=end_date)
# print("Before", len(dataYDay))
# dataYDay = dataYDay.drop(dataYDay.index[0])
# print("After ", len(dataYDay))
# print(data_today['VWAP'].head(2).mean())

#print(data_today.columns)
#vwap = data_today.loc[1]
#print(vwap)

#print(data_today[['VWAP', 'Close', 'Volume']].head(3))


#print(data_today.loc[2, 'VWAP'])
#print(dataYDay[['VWAP', 'Close', 'Volume']].tail(1))

#yDayVWAP = dataYDay[['VWAP', 'Close', 'Volume']].tail(1)
#print(yDayVWAP)

'''

'''
from Banknifty import BankniftyCls
from datetime import date

start_date = date(2023, 10, 17)
end_date = date(2023, 10, 20)
bn = BankniftyCls()
bndata = bn.get_BNData()
bndata.to_csv('file41.csv', header=True, index=True)

print(bndata)

'''

'''
import math

# Define the number you want to round
number = 45340

# Round the number up to the nearest 100th place
rounded_number = (number // 100) * 100

print(rounded_number)
# Define the number you want to round
#number = 45567

# Round the number down to the nearest 100th place
rounded_number = (number // 100) * 100 +100

# Print the rounded number
print(rounded_number)


# Print the rounded number
#print(rounded_number)
'''

# currentData = bn.get_Candle(interval='1m', period='5m', look_back=2, latest=False)

# print(currentData)

# currentData.to_csv('file3.csv', header=True, index=True)
# sma5 = bndata['Close'].rolling(window=5).mean().tail(n=2)

'''
bndata['sma5'] = bndata['Close'].rolling(window=5).mean()
bndata['sma20'] = bndata['Close'].rolling(window=20).mean()
bndata['ema18'] = bndata['Close'].ewm(span=18).mean()
bndata['sma50'] = bndata['Close'].rolling(window=50).mean()




for data in bndata:
    vwap = data['VWAP']
    bn = BankniftyCls()
    yVWAP = bn.getYesterdayVWAP()
    golden = bn.calGoldenLevel(yVWAP, vwap)
    data['GoldenUpper'] = golden['GoldenUpper']
    data['Golden'] = golden['Golden']
    data['GoldenLower'] = golden['GoldenLower']

bndata = bndata.round(2)
bndata.to_csv('file2.csv', header=True, index=True)
print(bndata)
'''

'''
sma5 = sma5.reset_index()
sma5Latest = sma5.loc[0, 'Close']
ema18 = bndata['Close'].ewm(span=18).mean().tail(n=2)
ema18 = ema18.reset_index()
ema18Latest = ema18.loc[0, 'Close']

sma50 = bndata['Close'].rolling(window=50).mean().tail(n=2)
#print(bndata['Close'].rolling(window=50).mean().tail(n=50))

sma50 = sma50.reset_index()
sma50Latest = sma50.loc[0, 'Close']
print('SMA5:', sma5Latest, '\nEMA18:', ema18Latest, '\n SMA50:', sma50Latest)
'''

'''
#print(bnData)
for stock in self.banknifty_Stocks:
df = yf.download(tickers=stock, interval=interval, period=period, start=start, end=end)

# Calculate the total price multiplied by volume

df['Price'] = (df['High'] + df['Low']) / 2
df['Price_times_Volume'] = df['Price'] * df['Volume']

# Calculate the cumulative sum of (price * volume) and volume
df['Cumulative_Price_Volume'] = df['Price_times_Volume'].cumsum()
df['Cumulative_Volume'] = df['Volume'].cumsum()
df['VWAP'] = df['Cumulative_Price_Volume'] / df['Cumulative_Volume']

#Adding up the BN volume
bnData['Volume'] += df['Volume']

df['Price'] = (df['High'] + df['Low']) / 2
df['Price_times_Volume'] = df['Price'] * df['Volume']
'''
from datetime import date
from datetime import timedelta

# data = bn.get_BNDataWithGoldenZones()
# data.to_csv('file5.csv', header=True, index=True)

'''

import pandas as pd
deMatrix = pd.DataFrame()
deMatrix['TIME'] =['1m', '3m', '5m', '15m', '30m', '1h', '1d']
#decisionMatrix['CLOSE'] = [4000, 5000, 5000, 566.6, 677,456, 67, 678]

deMatrix['CLOSE'] = [4000, 5000, 5000, 566.6666, 677, 456, 67]
#deMatrix['CLOSE'].add(77888)
deMatrix['OPEN'] = [6000, 4000, 56, 456.4444, 7924, 576, 1267]

deMatrix = deMatrix.round(2)
print(deMatrix)

condition = deMatrix['TIME'] == '15m'
result = deMatrix.loc[condition, 'CLOSE'].values[0]
print(result)

deMatrix.loc[condition, 'CLOSE'] = 8957.6
result = deMatrix.loc[condition, 'CLOSE'].values[0]
print(result)

print(deMatrix)


#print(deMatrix)
'''

'''
import yfinance as yf

# Define the ticker symbol and the date range
ticker_symbol = 'AAPL'  # Example: Apple Inc.
start_date = '2023-010-22'
end_date = '2022-12-31'
interval = '1d'  # Example: 1 day interval

# Fetch the data
data = yf.download(ticker_symbol, start=start_date, end=end_date, interval=interval)

# Print the fetched data
print(data)
'''
'''
import yfinance as yf
from datetime import datetime, timedelta

# Define the ticker symbol and the date for which you want the previous traded day
ticker_symbol = '^NSEBANK'  # Example: Apple Inc.
end_date = datetime.today() - timedelta(days=3)  # Previous traded day

# Fetch the data for the previous traded day
data = yf.download(ticker_symbol, end=end_date, period="1d")

# Print the fetched data
print(data)'''
'''
from datetime import datetime, timedelta
from nsepy import get_history

# Define the stock symbol and the date for which you want the previous traded day
stock_symbol = 'TCS'  # Example: Tata Consultancy Services
end_date = datetime.today() - timedelta(days=1)  # Previous traded day

# Fetch the data for the last traded day
data = get_history(symbol=stock_symbol, end=end_date, start=end_date, index=False)

# Print the fetched data
print(data)'''
import yfinance as yf
import pandas as pd
import ta as lib

#import pandas as pd
import numpy as np
def calculate_atr(data, period=9):
    data['H-L'] = data['High'] - data['Low']
    data['H-PC'] = abs(data['High'] - data['Close'].shift(1))
    data['L-PC'] = abs(data['Low'] - data['Close'].shift(1))

    data['TR'] = data[['H-L', 'H-PC', 'L-PC']].max(axis=1)
    atr = data['TR'].rolling(window=period, min_periods=1).mean()
    return atr


def SuperTrend(df, period=9, multiplier=1):
    atr = calculate_atr(df, period)
    hl2 = (df['High'] + df['Low']) / 2
    upperband = hl2 + (multiplier * atr)
    lowerband = hl2 - (multiplier * atr)

    final_upperband = upperband.copy()
    final_lowerband = lowerband.copy()

    for i in range(1, len(df)):
        if df['Close'][i - 1] > final_upperband[i - 1]:
            final_upperband[i] = max(upperband[i], final_upperband[i - 1])
        else:
            final_upperband[i] = upperband[i]

        if df['Close'][i - 1] < final_lowerband[i - 1]:
            final_lowerband[i] = min(lowerband[i], final_lowerband[i - 1])
        else:
            final_lowerband[i] = lowerband[i]

    supertrend = pd.Series(index=df.index)
    for i in range(len(df)):
        if df['Close'][i] <= final_upperband[i]:
            supertrend[i] = final_upperband[i]
        else:
            supertrend[i] = final_lowerband[i]

    df['SuperTrend'] = supertrend
    return df

from Banknifty import BankniftyCls
bank = BankniftyCls()

interval = '5m'
bndata = bank.get_BNData(interval=interval, period='5d')



SuperTrend(bndata)




'''
# Calculate RSI
#df['RSI'] = ta.momentum.rsi(close=df['Close'], window=9)

# Calculate Volume Weighted Moving Average (VWMA) on RSI
#vwma_rsi = ta.volume.VolumeWeightedAveragePrice(high=df['RSI'], low=df['RSI'], close=df['RSI'], volume=df['Volume'])
#df['VWMA_RSI'] = vwma_rsi.vwap

#print(df['VWMA_RSI'])

# Print the DataFrame with the VWMA on RSI
#print(df)


import pandas as pd
import ta
import matplotlib.pyplot as plt
import talib as talib

period = 20
deviation = 2.0
# Calculate the TTM Squeeze
#df['sma20'] = ta.trend.sma_indicator(close=df['Close'], window=20)
#df['sma20std'] = ta.volatility.bollinger_hband_indicator(close=df['Close'], window=20)
#df['sma20lstd'] = ta.volatility.bollinger_lband_indicator(close=df['Close'], window=20)
import pandas as pd
import ta
import matplotlib.pyplot as plt


# Calculate Bollinger Bands and Keltner Channel
df['bb_high'], df['bb_mid'], df['bb_low'] = ta.volatility.bollinger_hband(df['Close']), ta.volatility.bollinger_mavg(df['Close']), ta.volatility.bollinger_lband(df['Close'])
df['kc_high'], df['kc_mid'], df['kc_low'] = ta.volatility.keltner_channel_hband(df['High'], df['Low'], df['Close']), ta.volatility.keltner_channel_mband(df['High'], df['Low'], df['Close']), ta.volatility.keltner_channel_lband(df['High'], df['Low'], df['Close'])

# TTM Squeeze calculation
df['ttm_squeeze'] = (df['bb_high'] - df['bb_low']) / df['kc_high']

# Plotting the TTM Squeeze as a histogram
plt.figure(figsize=(10,6))
plt.bar(df.index, df['ttm_squeeze'], color='b', alpha=0.7)
plt.title('TTM Squeeze Histogram')
plt.xlabel('Index')
plt.ylabel('TTM Squeeze Value')
plt.show()
'''

'''
import numpy as np
import matplotlib.pyplot as plt

# Assuming 'close', 'high', and 'low' are arrays of corresponding values

from Banknifty import BankniftyCls

bank = BankniftyCls()
data = bank.get_BNData(period='5d')

#ticker = 'AAPL'
#data = yf.download(ticker, period='1d', interval='5m')

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import talib as talib

import ta as ta

# Fetch data for a particular ticker
#ticker = 'AAPL'
#data = yf.download(ticker, period='1d', interval='5m')

length = 20

# Function definitions
def sma(data, length):
    return data.rolling(window=length).mean()

def stdev(data, length):
    return data.rolling(window=length).std()

# Resample data to 5-minute interval
#data = data.resample('5T').mean()

# Calculate Bollinger Bands

data['SMA'] = sma(data['Close'], length)
data['std_dev'] = stdev(data['Close'], length)
data['UpperBand'] = data['SMA'] + 2 * data['std_dev']
data['LowerBand'] = data['SMA'] - 2 * data['std_dev']

# Define the period
length = 20

# Function to calculate Exponential Moving Average (EMA)
def ema(data, window):
    return data.ewm(span=window, adjust=False).mean()

# Calculate the middle line of the Keltner Channel
data['MiddleLine'] = ema(data['Close'], length)

# Calculate True Range (TR)
data['TR'] = np.maximum(data['High'] - data['Low'], abs(data['High'] - data['Close'].shift(1)), abs(data['Low'] - data['Close'].shift(1)))

# Calculate Average True Range (ATR)
data['ATR'] = data['TR'].ewm(span=length, adjust=False).mean()

# Define multiplier
multiplier = 2

# Calculate the upper and lower bands
data['kUpperBand'] = data['MiddleLine'] + multiplier * data['ATR']
data['kLowerBand'] = data['MiddleLine'] - multiplier * data['ATR']

#kchannel = ta.wrapper.KeltnerChannel(high=data['High'], low=data['Low'], close=data['Close'], window=20, window_atr=20,fillna=False,original_version=True, multiplier=2)

#data['KUP'] = kchannel.keltner_channel_hband()
#data['KLOW'] = kchannel.keltner_channel_lband()
#data['KMID'] = kchannel.keltner_channel_mband()

# Calculate TTM Squeeze
data['osc'] = (data['kUpperBand'] - data['kLowerBand']) / data['Close']
data['osc_color'] = np.where(data['osc'] < 0, '#00ffff', '#cc00cc')

data['diff'] = data['Close'] - ( (data['MiddleLine'] + data['SMA']) / 2 )

data['TTMSQ'] = (data['UpperBand'] < data['kUpperBand']) & (data['LowerBand'] > data['kLowerBand'])



data.to_csv('11.csv', header=True, index=True)
'''
'''
from Indicator import Indicator

def getPreviousIRB(sameDay=True, lookBack=60):
    ind = Indicator()
    data5 = ind.getSignals()
    low = data5.iloc[-2]['Low']
    high = data5.iloc[-2]['High']

    if sameDay:

        data5.index = pd.to_datetime(data5.index)
        # criteria = data5.index.strftime('%Y-%m-%d')

        # criteria = data5.index.strftime('%Y-%m-%d')

        # data5.index = data5.index.strftime('%Y-%m-%d')

        # Find the index of the row with the latest date
        latest_date = data5.index[-1].date()
        # latestDate = datetime.strptime(latest_date, "%Y-%m-%d")
        # latest_date_index = latestDate.strftime('%Y-%m-%d')

        # Convert the target date string to a datetime object
        # target_date = pd.to_datetime(latestDate)

        # Filter the DataFrame based on the target date
        latest_date_records = data5[data5.index.date == latest_date]

        # Extract the records with the latest date
        # latest_date_records = data5.loc[latest_date_index]

        length = len(latest_date_records)
        count = 1

        for i in range(length - 2, -1, -1):
            if count < lookBack:
                row = latest_date_records.iloc[i]
                irbLong = row['IRBLONG']
                irbShort = row['IRBSHORT']

                if irbLong or irbShort:
                    high = row['High']
                    low = row['Low']
                    break
                count += 1

        # data5.index = data5.index.strftime('%Y-%m-%d %H:%M:%S')

    return high, low

high, low = getPreviousIRB()
print(high, low)


from datetime import datetime
from Indicator import Indicator
import pytz

ind = Indicator()
data = ind.getSignals()

ind.setVWAP(data)

#data.index = pd.to_datetime(data.index)
timestamp = data.index[-1]
date_format = '%Y-%m-%d %H:%M:%S'

datetime_object = datetime.strptime(timestamp, date_format)

#datetime_object = datetime.utcfromtimestamp(timestamp.timestamp())

IST = pytz.timezone('Asia/Kolkata')
current_time = ist_time = datetime.now(IST)

#date_format = '%Y-%m-%d %H:%M:%S'

#datetime_object = datetime.strptime(index, date_format)

diff = current_time - datetime_object

threshold_time_difference = timedelta()

'''

'''
from Derivatives import NSE
from Util import logger
from TradeTrigger import TradeTrigger

nse = NSE()
name = 'BANKNIFTY'
price = 47400
strikePrice = 'PE_strikePrice'
identifier = 'PE_identifier'
bank_nifty_option_chain = nse.get_option_chain(
    ticker=name,
    is_index=True
)
print(bank_nifty_option_chain)

inmoney = bank_nifty_option_chain[bank_nifty_option_chain[strikePrice] == price][identifier].values[0]
call_ohlc = nse.get_ohlc_data(inmoney, timeframe='5Min', is_index=True)

df = nse.get_second_wise_data(ticker_or_index=inmoney,is_index=True, underlying_symbol=None )

print(call_ohlc)
#data = nse.get_raw_option_chain(ticker=name)
#data = nse.get_second_wise_data()
#nse.get_equity_options_trade_info()
#print(data)
#bank_nifty_option_chain[bank_nifty_option_chain[strikePrice] ==
 #                                              strikePrice]
#https://pypi.org/project/kitetrader/

'''

from kite_trade import *

# # First Way to Login
# # You can use your Kite app in mobile
# # But You can't login anywhere in 'kite.zerodha.com' website else this session will disconnected
'''
user_id = "NT1462"       # Login Id
password = "kite@1407"      # Login password
twofa = "480344"         # Login Pin or TOTP

enctoken = get_enctoken(user_id, password, twofa)
'''

'''
token = 'cfoRiDzIBiAvVEXxXLssc3f/K+mJPeS9zpHr6nV3r3b30AhCcXU4uEDlbsgrFaSHZGN9cEga+iIhQ3cZuik65TiYw1NgfNBKoXod57qLPdo32x3b1f6t8g=='
kite = KiteApp(enctoken=token)

print(kite.ltp(["NSE:NIFTY 50", "NFO:BANKNIFTY2410348300CE"]))

# Get Historical Data
import datetime
instrument_token = 11991042
from_datetime = datetime.datetime.now() - datetime.timedelta(days=1)     # From last & days
to_datetime = datetime.datetime.now()
interval = "minute"


data = pd.DataFrame(kite.historical_data(instrument_token, from_datetime, to_datetime, interval, continuous=False, oi=False))
data.to_csv("data.csv",header=True, index=True)

print(data)

#https://www.youtube.com/watch?v=Pz2GGsf0gps


from Zerodha import *
from pyotp import TOTP

user_id = "NT1462"  # Login Id
password = "kite@1407"  # Login password
# twofa = "245176"         # Login Pin or TOTP
totp_key = "QBI7DT2O23PYPAQOLX7N2SJ4HFWATBMJ"
otp = TOTP(totp_key).now()
print(otp)
login_with_credentials(user_id, password, otp)

# login_with_credentials(user_id, password, twofa)


with open("enctoken.txt") as f1:
    enctoken = f1.read()
kite = KiteApp(api_key="sxc1c2ygbmrvq6xd", userid=user_id, enctoken=enctoken)
print(kite.ltp(["NSE:NIFTY 50", "NFO:BANKNIFTY2410348300CE"]))

print('test')


from Indicator import Indicator

ind = Indicator()
data = ind.getSignals()
'''

'''
from neo_api_client import NeoAPI



def on_message(message):
    print(message)


def on_error(error_message):
    print(error_message)


client = NeoAPI(consumer_key="ejEVATnJJg6JlmT1jDrdaAPePSwa", consumer_secret="rb1Ux2JV_Gs6MjhMBRQCyXWPLzwa",
                environment='prod', on_message=on_message, on_error=on_error, on_close=None, on_open=None)

mpin='140779'
client.login(mobilenumber="+919890400707", password="Neo@1407", mpin=mpin)

# Complete login and generate session token
client.session_2fa(OTP= mpin)


print(client.order_report())

print('Done')
'''

import pandas as pd
import yfinance as yf

# Define the path to the Excel file containing NSE stock symbols
excel_file_path = 'Bullish with IRB, Technical Analysis Scanner.xlsx'

# Read the Excel file
df = pd.read_excel(excel_file_path)

# Extract the column with stock names
stock_names = df['Symbol']


# Function to check the specified conditions
def check_conditions(stock_data):
    if len(stock_data) < 2:
        return False

    close = stock_data['Close'].iloc[-2]
    open = stock_data['Open'].iloc[-2]
    high = stock_data['High'].iloc[-2]
    low = stock_data['Low'].iloc[-2]

    sma_5 = stock_data['Close'].rolling(window=5).mean().iloc[-2]
    sma_20 = stock_data['Close'].rolling(window=20).mean().iloc[-2]
    ema_18 = stock_data['Close'].ewm(span=18, adjust=False).mean().iloc[-2]

    condition1 = ((open - low) > (high - low) * 0.45) and (close > open) and (sma_5 > ema_18) and (close > sma_20) and (
                close > sma_5)
    condition2 = ((high - close) > (high - low) * 0.45) and (close > open) and (sma_5 > ema_18) and (
                close > sma_20) and (close > sma_5)
    condition3 = ((close - low) > (high - low) * 0.45) and (close < open) and (sma_5 > ema_18) and (
                close > sma_20) and (close > sma_5)
    condition4 = ((close - low) > (high - low) * 0.45) and (close < open) and (close > sma_5) and (sma_5 > ema_18) and (
                close > sma_20)

    return condition1 or condition2 or condition3 or condition4


# Initialize an empty list to store the results
results = []

# Loop through each stock symbol and fetch the data
for stock in stock_names:
    stock_info = yf.Ticker(stock + ".NS")  # NSE stocks have the suffix .NS
    hist = stock_info.history(period="1mo")  # Fetching data for the last month

    # Check the conditions
    if check_conditions(hist):
        results.append(stock)

# Print the stocks that meet the conditions
print("Stocks that meet the conditions:", results)

# Save the results to a new Excel file
results_df = pd.DataFrame(results, columns=['Stock Name'])
output_file_path = '/mnt/data/filtered_nse_stocks.xlsx'
results_df.to_excel(output_file_path, index=False)

print(f"Filtered stock data has been saved to {output_file_path}")