# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.



from Technical import NSE
import pandas as pd

from nsepy.technicals import pivot_point


#nse = NSE()

#data = nse.get_ohlc_data(ticker_or_idx="NIFTY BANK", is_index=True, timeframe='30Min')
#print(data)


from Derivatives import NSE

derNse = NSE()

bank_nifty_option_chain = derNse.get_option_chain(
    ticker='BANKNIFTY',
    is_index=True
)

#derNse.get_last_traded_date()

#derNse.get_second_wise_data(ticker_or_index='OPTIDXBANKNIFTY26-10-2023CE43800.00',is_index=False)
#bank_nifty_option_chain.to_csv('file11.csv', header=True, index=True)


#GET THE OPTION DATA
from Banknifty import BankniftyCls
bn = BankniftyCls()

currentData = bn.get_Candle(interval='1m', period='5m')



# Fetching OHLC data of an option contract
strike = currentData.loc[1, 'Close'] # atm contract
strike = int((strike // 100) * 100)

call_ticker_symbol = bank_nifty_option_chain[bank_nifty_option_chain['CE_strikePrice'] == strike]['CE_identifier'].values[0]
put_ticker_symbol = bank_nifty_option_chain[bank_nifty_option_chain['PE_strikePrice'] == strike]['PE_identifier'].values[0]
print(f'Call Symbol = {call_ticker_symbol} and Put Symbol = {put_ticker_symbol}')
call_ohlc = derNse.get_ohlc_data(call_ticker_symbol, timeframe='5Min', is_index=True)
put_ohlc = derNse.get_ohlc_data(put_ticker_symbol, timeframe='5Min', is_index=True)


print(call_ohlc.head())
print(put_ohlc.head())
#data = derNse.get_index_futures_data(index_or_ticker="SBIN")
#print(data)
'''
def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.



from Technical import NSE
import pandas as pd

nse = NSE()
data = nse.get_ohlc_data(ticker_or_idx="NIFTY BANK", timeframe='30m', is_index=True)
print(data)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

import talib as ta

functions = ta.get_functions()
count = 0
for fun in functions:
    count+=1
    print(fun)
print(count)


import yfinance as yf

from datetime import date
from datetime import timedelta

import nsepy as nse

expiry = nse.get_expiry_date(2013, 10)

lookback = 50
end_date = date.today()
start_date = end_date - timedelta(lookback)
ticker = '^NSEBANK'

new_ex = date
for ex in expiry:
    print(type(ex))
    print(ex)
    new_ex = ex

# end_date = date(2023,9,30)


#data = yf.download(tickers=ticker, start=start_date, end=end_date)
#print(data)

symbol = "RELIANCE"
start_date =date(2023,9,1)
end_date = date(2023,9,30)

banknifty_fut_data = nse.get_history(symbol=symbol, start=start_date, end=end_date)
print(banknifty_fut_data)
'''
'''
import pandas as pd

# Create a sample DataFrame
data = {'Name': ['John', 'Anna', 'Peter', 'Linda'],
        'Age': [25, 30, 35, 28]}
df = pd.DataFrame(data)

# Get the second row
second_row = df.iloc[1]

# Get data in the 'Name' column for the second row
name_data = df.loc[1, 'Name']

# Print the second row
print("Second Row:")
print(second_row)

# Print data in the 'Name' column for the second row
print("\nData in 'Name' column for the second row:")
print(name_data)
'''

'''
import yfinance as yf
import pandas as pd

# Define the ticker symbol
ticker_symbol = 'AAPL'  # Example: Apple Inc.

# Define the start and end dates
start_date = '2021-01-01'
end_date = '2021-12-31'

# Download data with the specific timeframe and set the index as datetime
data = yf.download(ticker_symbol, period='1d', interval='5m')

# Convert the index to a datetime object
data.index = pd.to_datetime(data.index)
data.index = data.index.strftime('%Y-%m-%d %H:%M')

# Print the downloaded data

#data = data.transpose()
data.to_csv('file1.csv', header=True, index=True)

print(data)

'''

'''
from Banknifty import BankniftyCls
bn = BankniftyCls()
currentData = bn.get_Candle(interval='1m', period='5m', look_back=2, latest=False)
currentData.to_csv('file3.csv', header=True, index=True)
print(currentData)'''



#import yfinance as yf
#bn_ticker = '^NSEBANK'
'''
data = yf.download(tickers=bn_ticker, interval='5m', period='2d')
data['sma50']=data['Close'].rolling(window=50).mean()
data['sma5']=data['Close'].rolling(window=5).mean()
data['sma20'] = data['Close'].rolling(window=20).mean()
data['ema18'] = data['Close'].ewm(span=18).mean()


data = yf.download(tickers=bn_ticker, interval='30m', period='1d')
data['sma50']=data['Close'].rolling(window=50).mean()
data['sma5']=data['Close'].rolling(window=5).mean()
data['sma20'] = data['Close'].rolling(window=20).mean()
data['ema18'] = data['Close'].ewm(span=18).mean()
data.to_csv('file411.csv', header=True, index=True)

'''

'''
from tickerstore.store import TickerStore
from datetime import date

fetcher = TickerStore()
data = fetcher.historical_data("NSE:SBIN", date(2023,9,15),
                        date(2023,9,19), TickerStore.INTERVAL_DAY_1)

print(data)


'''

'''
# Define the ticker symbol
ticker_symbol = 'AAPL'  # Example: Apple Inc.

# Set the interval to 30 minutes
data = yf.download(ticker_symbol, period="1mo", interval="30m")

data.to_csv('file31.csv', header=True, index=True)
'''


'''
import pandas as pd

# Create a sample DataFrame
data = {'A': [1, 2, 3, 4, 5],
        'B': [6, 7, 8, 9, 10],
        'C': [11, 12, 13, 14, 15]}
df = pd.DataFrame(data)
print(df)
# Define the condition
condition = df['A'] > 2

# Calculate the cumulative sum of rows based on the condition
cumulative_sum = df.loc[condition, :].cumsum()

# Print the cumulative sum based on the condition
print("Cumulative sum of rows based on the condition:")
print(cumulative_sum)

'''