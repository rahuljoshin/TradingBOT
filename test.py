'''
import schedule
import time


\
def job():
    print("Job is running...")

# Schedule the job to run every second
schedule.every(1).seconds.do(job)

while True:
    # Run pending scheduled jobs
    schedule.run_pending()
    time.sleep(1)

'''

'''
from TelgramCom import TemBot
bot = TemBot()'''

#bot.sendMessage("this is a test message")

'''
#Dataframe tryouts

import pandas as pd

# Create a sample DataFrame
data = {'Name': ['John', 'Anna', 'Peter', 'Linda'],
        'Age': [25, 30, 35, 28]}
df = pd.DataFrame(data)

# Add an empty column using square bracket notation
df['NewColumn1'] = ''

# Add another empty column using the assign method
df = df.assign(NewColumn2='')
condition = df['Name'] == 'Peter'

df.loc[condition, 'NewColumn1'] = 8957.6

print('lehgth:', len(df['Name']))
for col in df['Name']:
        print(col)


# Print the DataFrame with the empty columns
print(df)

import dateutil.utils
import pandas as pd



# import talib as ta
# algo = IBullsBearsAlgo()
# algo.execute()
# ta.BBANDS()
# print(ta.get_functions())
# algo.execute()

import yfinance as yf
from datetime import timedelta

# from Banknifty import BankniftyCls
# bank = BankniftyCls()
# bn_ticker = '^NSEBANK'
# prev_working_day = dateutil.utils.today() - timedelta(days=2)  # Adjust for the weekend
# bnData = yf.download(tickers=bn_ticker, interval='5m', period='2d')
# df= bank.get_BNData(interval='1d', period='60d')

# print(df)

# algo.execute()

# data = algo.getSignals(interval='30m')


# data.to_csv('Signals.csv', header=True, index=True)
# buy, sell = algo.findIRB(43584.25,43877.5,43567.45,43723.05)
# print('BUY',buy, 'Sell', sell)


import talib as talib

import ta

#bn_ticker = '^NSEBANK'
#df = yf.download(tickers=bn_ticker, interval='5m', period='2d')


from Banknifty import BankniftyCls
bank = BankniftyCls()
df = bank.get_BNData(period='2d')
# Set the period and standard deviation values
period = 20
deviation = 2.0

bbFrame = pd.DataFrame()
# Calculating Bollinger Bands with specified period and standard deviation
bbFrame['upper_band'], bbFrame['mid_band'], bbFrame['lower_band'] = talib.BBANDS(df['Close'], timeperiod=period,
                                                                                 nbdevup=deviation, nbdevdn=deviation)

bbFrame['SAR'] = talib.SAR(high=df['High'], low=df['Low'])

bbFrame['RSI'] = talib.RSI(df['Close'], timeperiod=9)
bbFrame['EMA3'] = talib.EMA(bbFrame['RSI'], timeperiod=3)
bbFrame['WMA21'] = talib.WMA(bbFrame['RSI'], timeperiod=21)

# Calculate Volume Weighted Moving Average (VWMA) on RSI
vwma_rsi = ta.volume.VolumeWeightedAveragePrice(high=bbFrame['RSI'], low=bbFrame['RSI'], close=bbFrame['RSI'], volume=df['Volume'])
bbFrame['VWMA_RSI'] = vwma_rsi.vwap

stoch = ta.momentum.StochasticOscillator(high=df['High'], low=df['Low'], close=df['Close'], window=4, smooth_window=1)
bbFrame['%K'] = stoch.stoch()
bbFrame['%D'] = stoch.stoch_signal()

key = 'allin1'
bbFrame.to_csv(f'{str(key)}.csv', header=True, index=True)



import pandas as pd
import ta
import matplotlib.pyplot as plt

# Creating a sample DataFrame
bn_ticker = '^NSEBANK'
df = yf.download(tickers=bn_ticker, interval='5m', period='1d')

# Calculate Stochastic Oscillator
stoch = ta.momentum.StochasticOscillator(high=df['High'], low=df['Low'], close=df['Close'], window=4, smooth_window=1)
df['%K'] = stoch.stoch()
df['%D'] = stoch.stoch_signal()

df.to_csv('stoch.csv', header=True, index=True)

# Plotting the Stochastic Oscillator
plt.figure(figsize=(10,6))
plt.plot(df.index, df['%K'], label='%K')
plt.plot(df.index, df['%D'], label='%D')
plt.title('Stochastic Oscillator')
plt.xlabel('Index')
plt.ylabel('Value')
plt.legend()
plt.show()
'''


'''
import pandas as pd
import io

# Creating a sample DataFrame
data_outer = {'Name': ['John', 'Anna', 'Peter', 'Linda'],
              'Age': [28, 23, 25, 27]}
df_outer = pd.DataFrame(data_outer)

# Creating another DataFrame to be stored in a column
data_inner = {'City': ['New York', 'Paris', 'Berlin', 'London'],
              'Country': ['USA', 'France', 'Germany', 'UK']}
df_inner = pd.DataFrame(data_inner)

# Storing the inner DataFrame in a column of the outer DataFrame as a string
df_outer['Inner_DataFrame'] = df_inner.to_json(orient='records')

print(df_outer)
# Retrieving the DataFrame back from the JSON string
json_string = df_outer['Inner_DataFrame']
retrieved_df_inner = pd.read_json(io.StringIO(json_string[3]), orient='records')

print("Retrieved DataFrame:")
print(retrieved_df_inner)

'''

'''
# Fibonacci pivot points calculation example
def fibonacci_pivot_points(high, low, close):
    pivot = round((high + low + close) / 3, 2)
    bCPR = round((high + low)/2, 2)
    TCPR = round(pivot + (pivot-bCPR),2)
    s1 = round(pivot - (0.382 * (high - low)),2)
    s2 = round(pivot - (0.618 * (high - low)), 2)
    s3 = round(pivot - (1.0 * (high - low)),2)
    r1 = round(pivot + (0.382 * (high - low)),2)
    r2 = round(pivot + (0.618 * (high - low)),2)
    r3 = round(pivot + (1.0 * (high - low)),2)
    return TCPR, pivot, bCPR, s1, s2, s3, r1, r2, r3

from Banknifty import BankniftyCls
bn = BankniftyCls()
data = bn.get_Candle(period='2d', interval='1d', latest=False)
TCPR, pivot, BCPR, s1, s2, s3, r1, r2, r3 = fibonacci_pivot_points(data.loc[1,'High'], data.loc[1, 'Low'], data.loc[1, 'Close'])
print(TCPR, pivot, BCPR, s1, s2, s3, r1, r2, r3)
#bn.get_BNDataWithGoldenZonesForDay()

'''

'''
import pandas as pd

# Create a sample DataFrame
data = {'Name': ['John', 'Anna', 'Peter', 'Linda'],
        'Age': ['25', '30', '35', '28'],
        'Height': ['175.5', '162.3', '180.1', '155.9']}
df = pd.DataFrame(data)

# Convert all columns to float data type
for column in df.columns:
    df[column] = pd.to_numeric(df[column], errors='coerce')

# Print the DataFrame with the converted data types
print(df.dtypes)
print(df)
'''

'''
import numpy as np
import matplotlib.pyplot as plt

# Given data
#sma_values = np.array([43035.76, 43018.15, 42989.17, 42955.85, 42918.85, 42880.48, 42862.33, 42843.63, 42840.72, 42805.99, 42780.74, 42766.13, 42751.03, 42750.27, 42735.67, 42722.16, 42703.37, 42683.9, 42671.15, 42673.03, 42680.69, 42690.08, 42704.67, 42714.4, 42708.07, 42706.67, 42704.23, 42694.73, 42686.32, 42684.88, 42673.5, 42668.25, 42663.06, 42656.44, 42652.46])
sma_values = np.array([42683.87, 42683.135, 42683.3425, 42682.8275, 42682.2125, 42682.8275, 42685.7225, 42687.565, 42690.9425, 42692.8675, 42693.9875, 42695.2775, 42697.4475, 42698.97, 42701.03, 42702.9025, 42703.6725, 42701.7775, 42701.005, 42698.73, 42697.4675, 42696.315, 42694.77, 42696.025, 42694.7375, 42692.2425, 42689.305, 42686.05, 42682.38, 42679.8925, 42678.725, 42677.135, 42675.76, 42675.44, 42675.085, 42675.615, 42677.995, 42680.12, 42682.0225])
sma_values = np.array([43500, 43500, 44000])
#sma_values = np.array([42750.76, 42750.15, 42750.17, 42750.85, 42750.85, 42750.48, 42750.33, 42750.63, 42840.72, 42750.99, 42780.74, 42750.13, 42751.03])
#sma_values = np.array([43000, 42500])
# Generating x-values based on the index of the SMA values
x_values = np.arange(len(sma_values))

# Performing linear regression
coefficients = np.polyfit(x_values, sma_values, 1)

# Extracting the slope (trend angle)
slope = coefficients[0]
rad = np.arctan(slope)
# Calculating the trend angle in degrees
trend_angle_degrees = np.rad2deg(rad)

# Plotting the data points and the trend line
plt.figure(figsize=(10, 6))
plt.scatter(x_values, sma_values, color='b', label='Data Points')
#plt.plot(x_values, slope * x_values + coefficients[1], color='r', label='Trend Line')

# Display the line segments contributing to the angle
plt.plot([x_values[0], x_values[-1]], [sma_values[0], sma_values[-1]], linestyle='dashed', color='g', label='Line 1')
plt.plot([x_values[0], x_values[-1]], [slope * x_values[0] + coefficients[1], slope * x_values[-1] + coefficients[1]], linestyle='dotted', color='m', label='Line 2')

# Adding title and labels
plt.title('Trend Angle with Data Points')
plt.xlabel('Index')
plt.ylabel('SMA Values')

# Adding legend
plt.legend()

# Display the plot
plt.show()

# Print the trend angle in degrees
print(f"The trend angle for the data points is: {trend_angle_degrees} degrees")

'''