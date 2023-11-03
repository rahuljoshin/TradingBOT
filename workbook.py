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
import ta

'''
from Banknifty import BankniftyCls
bank = BankniftyCls()


bn_ticker = '^NSEBANK'
df = bank.get_BNData(period='2d')

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

