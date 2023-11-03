import pandas as pd

from Banknifty import BankniftyCls

from TelgramCom import TemBot

from datetime import date
from datetime import datetime, time
from datetime import timedelta
import numpy as np

import ta as ta

from Derivatives import NSE


class Indicator:

    def __init__(self):
        # [1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo]
        self.TCPR = self.pivot = self.BCPR = self.s1 = self.s2 = self.s3 = self.r1 = self.r2 = self.r3 = 0.0

        self.signalData = pd.DataFrame()

        self.signal_datas = {'1m': pd.DataFrame(),
                             '5m': pd.DataFrame(),
                             '15m': pd.DataFrame(),
                             '30m': pd.DataFrame(),
                             '1d': pd.DataFrame()}

        self.derNse = NSE()
        self.rData = pd.DataFrame()

    def execute(self):
        self.calculatePivotLevels()
        if self.allSignals():

            tmp_result = self.buyorSell()
            last_result = self.rData.iloc[-1]['result'] if len(self.rData) else ''
            if tmp_result != last_result:
                new_row = {'result': tmp_result, 'time': datetime.now()}

                # Create a new DataFrame with the new row
                new_df = pd.DataFrame(new_row, index=[0])

                # Concatenate the new DataFrame with the original DataFrame
                self.rData = pd.concat([self.rData, new_df], ignore_index=True)

        message = f"{'Result'} {len(self.rData)} {'is:'} {self.rData.iloc[-1]['result']} {'from'} {self.rData.iloc[-1]['time']}"
        bot = TemBot()
        bot.sendMessage(message)

        print(message)

    def buyorSell(self):
        result = 'WAIT'
        # Logic for deciding buy or sell
        time30 = '30m'
        data30 = self.signal_datas[time30]
        data30 = data30.reset_index()
        time5 = '5m'
        data5 = self.signal_datas[time5]
        data5 = data5.reset_index()

        buy30min = (((data30.iloc[-2]['Close'] > data30.iloc[-2]['EMA18']) or (
                data30.iloc[-2]['SMA5'] > data30.iloc[-2]['EMA18']))
                    and (data5.iloc[-2]['SMA5'] > data5.iloc[-2]['EMA18']) and (
                            data30.iloc[-2]['Close'] > data30.iloc[-2]['SMA20']))

        weakSell30min = (((data30.iloc[-2]['Close'] > data30.iloc[-2]['EMA18']) or (
                data30.iloc[-2]['SMA5'] > data30.iloc[-2]['EMA18']))
                         and (data5.iloc[-2]['SMA5'] < data5.iloc[-2]['EMA18']) and (
                                 data30.iloc[-2]['Close'] > data30.iloc[-2]['SMA20']))

        sell30min = (((data30.iloc[-2]['Close'] < data30.iloc[-2]['EMA18']) or (
                data30.iloc[-2]['SMA5'] < data30.iloc[-2]['EMA18']))
                     and (data5.iloc[-2]['SMA5'] < data5.iloc[-2]['EMA18']) and (
                             data30.iloc[-2]['Close'] < data30.iloc[-2]['SMA20']))

        weakBuy30min = (((data30.iloc[-2]['Close'] < data30.iloc[-2]['EMA18']) or (
                data30.iloc[-2]['SMA5'] < data30.iloc[-2]['EMA18']))
                        and (data5.iloc[-2]['SMA5'] > data5.iloc[-2]['EMA18']) and (
                                data30.iloc[-2]['Close'] < data30.iloc[-2]['SMA20']))

        buy5min = ((data5.iloc[-2]['Close'] > data5.iloc[-2]['SMA5']) and (
                data5.iloc[-2]['Close'] > data5.iloc[-2]['EMA18']) and (
                           data5.iloc[-2]['SMA5'] > data5.iloc[-2]['EMA18']) and (
                           data5.iloc[-2]['SMA5'] > data5.iloc[-2]['SMA20']) and (
                           data5.iloc[-2]['Close'] > data5.iloc[-2]['VWAP']))

        sell5min = ((data5.iloc[-2]['Close'] < data5.iloc[-2]['SMA5']) and (
                data5.iloc[-2]['Close'] < data5.iloc[-2]['EMA18']) and (
                            data5.iloc[-2]['SMA5'] < data5.iloc[-2]['EMA18']) and (
                            data5.iloc[-2]['SMA5'] < data5.iloc[-2]['SMA20']) and (
                            data5.iloc[-2]['Close'] < data5.iloc[-2]['VWAP']))

        if buy30min and buy5min:
            result = 'BESTBUY'
        elif sell30min and sell5min:
            result = 'BESTSELL'
        elif weakSell30min and sell5min:
            result = 'QUICKSELL'
        elif weakBuy30min and buy5min:
            result = 'QUICKBUY'

        return result

    def fixed_range_volume_profile(self, prices, volumes, num_levels):
        price_levels = np.linspace(min(prices), max(prices), num_levels)
        volume_profile = np.zeros(num_levels)

        for i in range(len(prices)):
            for j in range(num_levels - 1):
                if price_levels[j] <= prices[i] < price_levels[j + 1]:
                    volume_profile[j] += volumes[i]
                    break

        return price_levels, volume_profile

    def calculatePivotLevels(self):

        if self.TCPR == 0:
            print("Calculating pivot level")
            bank = BankniftyCls()
            data = bank.get_Candle(period='2d', interval='1d', latest=False)
            self.TCPR, self.pivot, self.BCPR, self.s1, self.s2, self.s3, self.r1, self.r2, self.r3 = (
                self.fibonacci_pivot_points(data.loc[1, 'High'], data.loc[1, 'Low'], data.loc[1, 'Close']))
            print("Calculating pivot done")

    def findIRB(self, open, high, low, close):
        data = pd.DataFrame()
        data['Open'] = open
        data['High'] = high
        data['Low'] = low
        data['Close'] = close

        z = 45.0
        # CandleRange
        data['a'] = abs(data['High'] - data['Low'])
        # Candle Body
        data['b'] = abs(data['Close'] - data['Open'])
        # PercenttoDecimal
        c = z / 100

        # RangeVerification
        data['rv'] = data['b'] < c * data['a']

        # PriceLevelfor Retracement
        data['x'] = data['Low'] + c * data['a']
        data['yy'] = data['High'] - c * data['a']

        data['goLong'] = (data['rv'] == True) & (data['High'] > data['yy']) & (data['Close'] < data['yy']) & (
                data['Open'] < data['yy'])
        data['goShort'] = (data['rv'] == True) & (data['Low'] < data['x']) & (data['Close'] > data['x']) & (
                data['Open'] > data['x'])

        # goLong = rv == True and high > yy and close < yy and open < yy
        # goShort = rv == True and low < x and close > x and open > x

        return data['goLong'], data['goShort']

    def fibonacci_pivot_points(self, high, low, close):
        pivot = round((high + low + close) / 3, 2)
        bCPR = round((high + low) / 2, 2)
        TCPR = round(pivot + (pivot - bCPR), 2)
        s1 = round(pivot - (0.382 * (high - low)), 2)
        s2 = round(pivot - (0.618 * (high - low)), 2)
        s3 = round(pivot - (1.0 * (high - low)), 2)
        r1 = round(pivot + (0.382 * (high - low)), 2)
        r2 = round(pivot + (0.618 * (high - low)), 2)
        r3 = round(pivot + (1.0 * (high - low)), 2)
        return TCPR, pivot, bCPR, s1, s2, s3, r1, r2, r3

    def allSignals(self):
        # count=1
        stat = False
        for key, value in self.signal_datas.items():
            if self.isRecalculate(str(key)):
                print('Find signals for', str(key), 'started')
                data = self.getSignals(interval=str(key))
                self.signal_datas[str(key)] = data
                stat = True
                data.to_csv(f'{str(key)}.csv', header=True, index=True)
                print('Find signals for', str(key), 'completed')

        return stat

    def isRecalculate(self, time):
        stat = False
        data = self.signal_datas[time]
        if len(data):
            if self.isWorkingHours():
                index = data.index[-1]
                current_time = datetime.now()
                date_format = '%Y-%m-%d %H:%M:%S'
                datetime_object = datetime.strptime(index, date_format)

                diff = current_time - datetime_object

                threshold_time_difference = timedelta()
                if time == '1m':
                    threshold_time_difference = timedelta(minutes=1)
                elif time == '5m':
                    threshold_time_difference = timedelta(minutes=5)
                elif time == '15m':
                    threshold_time_difference = timedelta(minutes=15)
                elif time == '30m':
                    threshold_time_difference = timedelta(minutes=30)
                elif time == '1d':
                    threshold_time_difference = timedelta(days=1)

                if diff > threshold_time_difference:
                    stat = True
        else:
            stat = True

            # current_time = current_time.strftime('%Y-%m-%d %H:%M')
            # index_time = index.strftime('%Y-%m-%d %H:%M')

        return stat

    def isWorkingHours(self):
        stat = False

        weekday = datetime.now().isoweekday()

        # Define the time range
        start_time = time(9, 15, 0)  # 9:15 AM
        end_time = time(15, 30, 0)  # 3:30 PM

        # Get the current time
        current_time = datetime.now().time()

        # Check if the current time is within the time range
        if start_time <= current_time <= end_time and weekday < 6:
            stat = True

        return stat

    def getSignals(self, interval='5m'):

        bank = BankniftyCls()
        bndata = pd.DataFrame()

        if interval == '1m' or interval == '5m':
            bndata = bank.get_BNData(interval=interval, period='2d')
        elif interval == '15m' or interval == '30m':
            bndata = bank.get_BNData(interval=interval, period='6d')
        elif interval == '1d':
            bndata = bank.get_BNData(interval=interval, period='60d')

        # bndata['BUYORSELL'] = 'WAIT'
        # bndata['IRBLONG'], bndata['IRBSHORT'] = 'FALSE', 'FALSE'
        # bndata['TTMSQ'] = 'FALSE'

        # PSAR, RSI9,3,21 and stocastics
        bndata['SAR'] = ta.wrapper.PSARIndicator(high=bndata['High'], low=bndata['Low'], close=bndata['Close']).psar()

        bndata['RSI9'] = ta.wrapper.RSIIndicator(close=bndata['Close'], window=9).rsi()
        bndata['EMA3_RSI'] = ta.wrapper.EMAIndicator(bndata['RSI9'], window=3).ema_indicator()

        # Calculate VWMA with a period of 21 on RSI
        bndata['VWMA21_RSI'] = self.vwma(bndata['RSI9'], bndata['Volume'], period=21)

        stoch = ta.momentum.StochasticOscillator(high=bndata['High'], low=bndata['Low'], close=bndata['Close'],
                                                 window=4,
                                                 smooth_window=1)
        bndata['%K'] = stoch.stoch()
        bndata['%D'] = stoch.stoch_signal()

        # SMA5,20,50 and EMA 18,50
        bndata['SMA5'] = bndata['Close'].rolling(window=5).mean()
        bndata['EMA18'] = bndata['Close'].ewm(span=18).mean()
        bndata['SMA20'] = bndata['Close'].rolling(window=20).mean()
        bndata['SMA50'] = bndata['Close'].rolling(window=50).mean()
        bndata['EMA50'] = bndata['Close'].ewm(span=50).mean()

        bndata['SMA50'].fillna(bndata['EMA50'], inplace=True)

        # Bollinger band 20,2
        bndata['BBUpperBand'], bndata['BBLowerBand'] = self.calBB(bndata['Close'], period=20, stdev=2)

        bndata['kUpperBand'], bndata['kMiddleLine'], bndata['kLowerBand'] = self.calculateKeltnerChannel(bndata['High'],
                                                                                                         bndata['Low'],
                                                                                                         bndata[
                                                                                                             'Close'],
                                                                                                         period=20,
                                                                                                         multiplier=2)

        bndata['TTMSQ'] = (bndata['BBUpperBand'] < bndata['kUpperBand']) & (
                bndata['BBLowerBand'] > bndata['kLowerBand'])

        bndata['diff'] = bndata['Close'] - ((bndata['kMiddleLine'] + bndata['SMA20']) / 2)

        bndata['tenkan'], bndata['kijun'], bndata['senkouA'], bndata['senkouB'] = self.calcSuperIchi(bndata['Close'],
                                                                                                     bndata['High'],
                                                                                                     bndata['Low'])

        bndata = bndata.round(2)

        bndata['IRBLONG'], bndata['IRBSHORT'] = self.findIRB(bndata['Open'], bndata['High'], bndata['Low'],
                                                             bndata['Close'])

        # bndata = bndata.fillna(-1)

        bndata['BUYORSELL'] = 'WAIT'
        bndata.loc[(bndata['Close'] > bndata['SMA5']) & (bndata['SMA5'] > bndata['EMA18']) & (
                bndata['Close'] > bndata['SMA20']) & (bndata['EMA18'] > bndata['SMA50']) & (
                           bndata['SMA5'] > bndata['SMA50']) & (bndata['SMA5'] > bndata['SMA20']) &
                   (bndata['Close'] > bndata['SMA50']), 'BUYORSELL'] = 'BUY'
        bndata.loc[(bndata['Close'] < bndata['SMA5']) & (bndata['SMA5'] < bndata['EMA18']) & (
                bndata['Close'] < bndata['SMA20']) & (bndata['EMA18'] < bndata['SMA50']) & (
                           bndata['SMA5'] < bndata['SMA50']) & (bndata['SMA5'] < bndata['SMA20']) &
                   (bndata['Close'] < bndata['SMA50']), 'BUYORSELL'] = 'SELL'

        return bndata

    # Function to calculate VWMA
    def vwma(self, rsi9, volume, period=21):
        typical_price = rsi9
        TPV = typical_price * volume
        CumulativeTPV = TPV.rolling(window=period).sum()
        CumulativeVolume1 = volume.rolling(window=period).sum()
        VWMA21_RSI = CumulativeTPV / CumulativeVolume1
        return VWMA21_RSI

    def calculateKeltnerChannel(self, high, low, close, period=20, multiplier=2):
        # Calculate True Range (TR)
        TR = np.maximum(high - low, abs(high - close.shift(1)),
                        abs(low - close.shift(1)))

        # Calculate Average True Range (ATR)
        ATR = TR.ewm(span=period, adjust=False).mean()

        # Calculate the middle line of the Keltner Channel
        kMiddleLine = close.ewm(span=period, adjust=False).mean()
        # Calculate the upper and lower bands
        kUpperBand = kMiddleLine + multiplier * ATR
        kLowerBand = kMiddleLine - multiplier * ATR

        osc = (kUpperBand - kLowerBand) / close
        osc_color = np.where(osc < 0, '#00ffff', '#cc00cc')

        # diff = close - ((kMiddleLine + SMA20) / 2)

        return kUpperBand, kMiddleLine, kLowerBand

    def calBB(self, close, period=20, stdev=2):
        std_dev = close.rolling(window=period).std()
        sma20 = close.rolling(window=period).mean()
        BBUpperBand = sma20 + stdev * std_dev
        BBLowerBand = sma20 - stdev * std_dev

        return BBUpperBand, BBLowerBand

    def findSuperVal(self, close, high, low, length, mult):
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

    def calcSuperIchi(self, close, high, low):

        # Define inputs
        tenkan_len = 9
        tenkan_mult = 2.0
        kijun_len = 26
        kijun_mult = 4.0
        spanB_len = 52
        spanB_mult = 6.0
        offset = 26

        # Calculate Tenkan-sen
        tenkan = self.findSuperVal(close, high, low, tenkan_len, tenkan_mult).values

        # Calculate Kijun-sen
        kijun = self.findSuperVal(close, high, low, kijun_len, kijun_mult).values

        # Calculate Senkou Span A and Senkou Span B
        senkouA = (kijun + tenkan) / 2
        senkouB = self.findSuperVal(close, high, low, spanB_len, spanB_mult).values

        return tenkan, kijun, senkouA, senkouB
