import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def bband(close, length, mult):
    return pd.Series(close.rolling(window=length).mean() + mult * close.rolling(window=length).std(), name='bband')

def keltner(close, tr, length, mult):
    return pd.Series(close.ewm(span=length, min_periods=length).mean() + mult * tr.ewm(span=length, min_periods=length).mean(), name='keltner')

def calculate_true_range(data):
    high = data['High']
    low = data['Low']
    close = data['Close']

    # Calculate the True Range
    tr = pd.DataFrame(index=data.index)
    tr['hl'] = high - low
    tr['h_c'] = abs(high - close.shift(1))
    tr['l_c'] = abs(low - close.shift(1))
    tr['true_range'] = tr[['hl', 'h_c', 'l_c']].max(axis=1)

    return tr['true_range']

def study(data, length=20):
    high = data['High']
    low = data['Low']
    close = data['Close']
    tr = calculate_true_range(data)  # You need to calculate or have the true range (tr) in your data

    e1 = (high.rolling(window=length).max() + low.rolling(window=length).min()) / 2 + close.rolling(window=length).mean()

    osc = pd.Series((close - e1 / 2).rolling(window=length).apply(lambda x: np.polyfit(np.arange(len(x)), x, 1)[0], raw=True), name='osc')
    osc = osc.dropna()
    #val = osc.values
    #print(val)

    diff = bband(close, length, 2) - keltner(close, tr, length, 1)
    diff = diff.dropna()
    print(diff)
    osc_color = np.where((osc.shift(1) < osc) & (osc >= 0), '#00ffff', np.where(osc >= 0, '#009b9b', '#cc00cc'))
    mid_color = np.where(diff >= 0, 'g', 'r')

    print("Length of osc:", len(osc))
    print("Length of osc_color:", len(osc_color))

    plt.plot(osc.values, color=osc_color, linestyle='-', linewidth=2)
    plt.plot(np.zeros_like(osc.values), color=mid_color, marker='o', markersize=3, linestyle='None')

    plt.show()

from Banknifty import BankniftyCls
bank = BankniftyCls()


df = bank.get_BNData(period='2d')
study(df)

'''
from Indicator import Indicator
from TradeTrigger import TradeTrigger

ind = Indicator()
data = ind.getSignals()
ind.newSignalData['5m'] = ind.newSignalData['5m']._replace(data=data)

trade = TradeTrigger()
trade.execute(ind)

trade.getPreviousIRB()




from Indicator import Indicator
ind = Indicator()
ind.inTopVolumeZone()


from TradeTrigger import TradeTrigger
trade = TradeTrigger()
trade.recordTrade()

# Fetch data for a particular ticker
ticker = 'NIFTY BANK'
# data = yf.download(ticker, period='1mo', interval='1d')

from Banknifty import BankniftyCls

bank = BankniftyCls()
data = bank.get_BNData(period='2d')
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Fetch data for a particular ticker
# ticker = 'AAPL'
# data = yf.download(ticker, period='1mo', interval='1d')

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# Define the period
length = 20

# Function definitions
def sma(data, length):
    return data.rolling(window=length).mean()

def stdev(data, length):
    return data.rolling(window=length).std()

def ema(data, length):
    return data.ewm(span=length, adjust=False).mean()

# Calculate Bollinger Bands
def bband(data, length, mult=2):
    return sma(data, length) + mult * stdev(data, length)

# Calculate Keltner Channels
def keltner(close, high, low, length, mult=1):
    tr = np.maximum(high - low, abs(high - close.shift(1)), abs(low - close.shift(1)))
    return ema(close, length) + mult * ema(tr, length)

# Calculate TTM Squeeze
data['e1'] = (data['High'].rolling(window=length).max() + data['Low'].rolling(window=length).min()) / 2 + sma(data['Close'], length)
data['osc'] = np.polyfit(np.arange(len(data)), (data['Close'] - data['e1'] / 2), 1)[0]
data['diff'] = bband(data['Close'], length, 2) - keltner(data['Close'], data['High'], data['Low'], length, 1)
data['osc_color'] = np.where((data['osc'].shift(1) < data['osc']) & (data['osc'] >= 0), '#00ffff', np.where((data['osc'].shift(1) < data['osc']) & (data['osc'] < 0), '#cc00cc', np.where((data['osc'].shift(1) >= data['osc']) & (data['osc'] >= 0), '#009b9b', '#ff9bff')))
data['mid_color'] = np.where(data['diff'] >= 0, 'green', 'red')

# Plotting histogram for 'osc' column and circles for 'mid_color'
plt.figure(figsize=(8,6))
plt.hist(data['osc'].dropna(), color='#6495ED', alpha=0.7, bins=30, edgecolor='black')

plt.plot(np.arange(len(data)), np.zeros(len(data)), color=data['mid_color'], marker='o', linestyle='', markersize=10)
plt.title('TTM Squeeze Indicator for {}'.format(ticker))
plt.xlabel('Date')
plt.ylabel('Value')
plt.show()



from iBullsBearsAlgo import IBullsBearsAlgo
algo = IBullsBearsAlgo()
signals = algo.getSignals()

signals.to_csv('test.csv', header=True, index=True)


'''
'''

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Fetch data for a particular ticker
#ticker = 'AAPL'
#data = yf.download(ticker, period='1mo', interval='1d')

from Banknifty import BankniftyCls

bank = BankniftyCls()
data = bank.get_BNData(period='2d')

# Define inputs
tenkan_len = 9
tenkan_mult = 2.0
kijun_len = 26
kijun_mult = 4.0
spanB_len = 52
spanB_mult = 6.0
offset = 26


# Function to calculate average
def avg(close, high, low, length, mult):
    atr = (high - low).rolling(window=length).mean() * mult
    up = (high + low) / 2 + atr
    dn = (high + low) / 2 - atr
    upper = pd.Series(np.zeros(len(close)))
    lower = pd.Series(np.zeros(len(close)))
    os = 0
    max_val = pd.Series(np.zeros(len(close)))
    min_val = pd.Series(np.zeros(len(close)))
    for i in range(1, len(close)):
        if close.iloc[i - 1] < upper.iloc[i - 1]:
            upper.iloc[i] = min(up.iloc[i], upper.iloc[i - 1])
        else:
            upper.iloc[i] = up.iloc[i]
        if close.iloc[i - 1] > lower.iloc[i - 1]:
            lower.iloc[i] = max(dn.iloc[i], lower.iloc[i - 1])
        else:
            lower.iloc[i] = dn.iloc[i]

        if close.iloc[i] > upper.iloc[i]:
            os = 1
        elif close.iloc[i] < lower.iloc[i]:
            os = 0

        if os == 1:
            spt = lower.iloc[i]
        else:
            spt = upper.iloc[i]

        if close.iloc[i] > spt:
            max_val.iloc[i] = max(close.iloc[i], max_val.iloc[i - 1])
        elif os == 1:
            max_val.iloc[i] = max(close.iloc[i], max_val.iloc[i - 1])
        else:
            max_val.iloc[i] = spt

        if close.iloc[i] < spt:
            min_val.iloc[i] = min(close.iloc[i], min_val.iloc[i - 1])
        elif os == 0:
            min_val.iloc[i] = min(close.iloc[i], min_val.iloc[i - 1])
        else:
            min_val.iloc[i] = spt

    return (max_val + min_val) / 2


# Calculate Tenkan-sen
d = avg(data['Close'], data['High'], data['Low'] , tenkan_len, tenkan_mult)
data['tenkan'] = d.values
# Calculate Kijun-sen
data['kijun'] = avg(data['Close'], data['High'], data['Low'], kijun_len, kijun_mult).values

# Calculate Senkou Span A and Senkou Span B
data['senkouA'] = (data['kijun'] + data['tenkan']) / 2
data['senkouB'] = avg(data['Close'], data['High'], data['Low'], spanB_len, spanB_mult).values
data.to_csv('super.csv', header=True, index=True)
'''
'''
# Plotting
plt.plot(tenkan, label='Tenkan-Sen', color='#2157f3')
plt.plot(kijun, label='Kijun-Sen', color='#ff5d00')
plt.fill_between(data.index, senkouA, senkouB, where=senkouA > senkouB, color='teal', alpha=0.8)
plt.fill_between(data.index, senkouA, senkouB, where=senkouA <= senkouB, color='red', alpha=0.8)
plt.legend()
plt.show()
'''

'''
from iBullsBearsAlgo import IBullsBearsAlgo
algo = IBullsBearsAlgo()
signals = algo.getSignals()

signals.to_csv('test11.csv', header=True, index=True)

from Banknifty import BankniftyCls
import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Fetch data for a particular ticker
#ticker = 'AAPL'
#data = yf.download(ticker, period='1mo', interval='1d')

bank = BankniftyCls()
data = bank.get_BNData(period='2d')

start_date = '2023-11-01 11:45:00'
end_date = '2023-11-01 14:55:00'



# Calculate SMA
data['SMA'] = data['Close'].rolling(window=20).mean()
data = data.loc[start_date:end_date]
#data = data.iloc[[0,-1]]
#data = data.iloc[-6:-1]
data = data.dropna()
# Fit linear regression
x = np.arange(len(data))
y = data['SMA'].values
coefficients = np.polyfit(x, y, 1)
slope = coefficients[0]
rad = np.arctan(slope)
# Calculate angle in degrees
angle = np.degrees(rad)

#a= np.rad2deg(np.arctan(slope))
# Plotting
plt.plot(data.index, data['SMA'], label='SMA')
plt.title('Simple Moving Average (SMA) with Angle ' + str(angle) + ' degrees')
plt.legend()
plt.show()

from Banknifty import BankniftyCls
from Indicator import Indicator
algo = Indicator()
bank = BankniftyCls()

algo.getSignals()'''
#records = algo.getSignals(data)
#records.to_csv('record.csv', header=True, index=True)
'''
bank = BankniftyCls()
data = bank.get_BNData()
d= pd.DataFrame()
price_data, volume_data = algo.fixed_range_volume_profile(prices=data['Close'], volumes=data['Volume'], num_levels=10)

import heapq


# Create a list of tuples containing price and volume data
data = list(zip(price_data, volume_data))

# Get the top 3 records based on the volume data in cloumn 1
top_3_records = heapq.nlargest(3, data, key=lambda x: x[1])

# Print the top 3 records
print("The top 3 records based on the volume profile are:")
for record in top_3_records:
    print(f"Price: {record[0]}, Volume: {record[1]}")

print(d)
#algo.allSignals()
'''