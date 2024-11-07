import numpy as np
import pandas as pd
import ta as lib
from ta.trend import PSARIndicator
import ta.volatility


class IndHelper:

    @staticmethod
    def fixed_range_volume_profile(prices, volumes, num_levels=10):
        price_levels = np.linspace(min(prices), max(prices), num_levels)
        digitized = np.digitize(prices, price_levels)

        volume_profile = np.zeros(num_levels)

        for i in range(len(prices)):
            bin_index = digitized[i] - 1
            volume_profile[bin_index] += volumes.iloc[i]

        rounded_price_levels = np.round(price_levels, decimals=2)

        return rounded_price_levels, volume_profile

    @staticmethod
    def calBB(close, period=20, stddev=2):
        std_dev = close.rolling(window=period).std()
        sma20 = close.rolling(window=period).mean()
        BBUpperBand = sma20 + stddev * std_dev
        BBLowerBand = sma20 - stddev * std_dev
        return BBUpperBand, BBLowerBand

    @staticmethod
    def getSAR(high, low, close):

        sarValues = PSARIndicator(high=high.squeeze(), low=low.squeeze(),
                                  close=close.squeeze()).psar()
        return sarValues

    @staticmethod
    def getRSI(close, window=9):

        rsiValues = lib.wrapper.RSIIndicator(close=close.squeeze(), window=window,fillna=True).rsi()
        return rsiValues

    @staticmethod
    def getEMA(close, window=9):

        emaValues = lib.wrapper.EMAIndicator(close=close.squeeze(), window=window, fillna=True).ema_indicator()
        return emaValues

    @staticmethod
    def calculateKeltnerChannel(high, low, close, period=20, multiplier=1.5):
        # Calculate True Range (TR)

        # Calculate the Exponential Moving Average (EMA)
        ema = close.ewm(span=period, adjust=False).mean()

        # Calculate the Average True Range (ATR)
        atr = ta.volatility.AverageTrueRange(high=high, low=low, close=close,
                                                       window=period).average_true_range()

        # Calculate the Keltner Channel Bands
        kUpperBand = ema + (atr * multiplier)
        kLowerBand = ema - (atr * multiplier)
        return kUpperBand, ema, kLowerBand

    @staticmethod
    def calcSuperIchi(close, high, low):
        # Define inputs
        tenkan_len = 9
        tenkan_mult = 2.0
        kijun_len = 26
        kijun_mult = 4.0
        spanB_len = 52
        spanB_mult = 6.0
        offset = 26

        high = high.squeeze()
        low = low.squeeze()
        close = close.squeeze()

        tenkan = IndHelper.avgNew(close, high, low, tenkan_len, tenkan_mult)
        kijun = IndHelper.avgNew(close, high, low, kijun_len, kijun_mult)
        senkouA = np.nanmean([kijun, tenkan], axis=0)
        senkouB = IndHelper.avgNew(close, high, low, spanB_len, spanB_mult)

        '''
        data = {'close': close, 'high': high, 'low': low}  # Replace with your actual data
        src = pd.DataFrame(data)
        tenkan = IndHelper.avg1(src, tenkan_len, tenkan_mult)
        kijun = IndHelper.avg1(src, kijun_len, kijun_mult)

        senkouA = np.nanmean([kijun, tenkan], axis=0)
        senkouB = IndHelper.avg1(src, spanB_len, spanB_mult)
        '''

        return tenkan, kijun, senkouA, senkouB

    @staticmethod
    def avg1(src, length, mult):
        atr = (src['high'] - src['low']).rolling(window=length).mean() * mult

        up = (src['high'] + src['low']) / 2 + atr
        dn = (src['high'] + src['low']) / 2 - atr
        upper, lower = 0.0, 0.0

        upper = np.where(src['close'].shift(1) < upper, np.minimum(up, upper), up)
        lower = np.where(src['close'].shift(1) > lower, np.maximum(dn, lower), dn)

        os, max_val, min_val = 0, src['close'].iloc[0], src['close'].iloc[0]

        os = np.where(src['close'] > upper, 1, np.where(src['close'] < lower, 0, os))
        spt = np.where(os == 1, lower, upper)

        shifted_max_val = np.roll(max_val, 1)

        max_val = np.where(
            np.where(src['close'] > spt, True, False),
            np.maximum(src['close'], shifted_max_val),
            np.where(
                os == 1,
                np.maximum(src['close'], shifted_max_val),
                spt
            )
        )

        shifted_min_val = np.roll(min_val, 1)

        min_val = np.where(
            np.where(src['close'] > spt, True, False),
            np.minimum(src['close'], shifted_min_val),
            np.where(
                os == 0,
                np.minimum(src['close'], shifted_min_val),
                spt
            )
        )
        return np.nanmean([max_val, min_val], axis=0)

    @staticmethod
    def findIRB(open, high, low, close):
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

        # PriceLevel for Retracement
        data['x'] = data['Low'] + c * data['a']
        data['yy'] = data['High'] - c * data['a']

        data['goLong'] = (data['rv'] == True) & (data['High'] > data['yy']) & (data['Close'] < data['yy']) & (
                data['Open'] < data['yy'])
        data['goShort'] = (data['rv'] == True) & (data['Low'] < data['x']) & (data['Close'] > data['x']) & (
                data['Open'] > data['x'])

        # goLong = rv == True and high > yy and close < yy and open < yy
        # goShort = rv == True and low < x and close > x and open > x

        return data['goLong'], data['goShort']

    @staticmethod
    def findSuperVal(close, high, low, length, mult):
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

    @staticmethod
    def getStoch(high, low, close, window, smooth_window):

        stoch = lib.wrapper.StochasticOscillator(high=high.squeeze(), low=low.squeeze(), close=close.squeeze(),
                                                 window=window, smooth_window=smooth_window)
        return stoch.stoch(), stoch.stoch_signal()

    @staticmethod
    def avgNew(src, high, low, length, mult):

        hl2 = (high + low) / 2

        atr_values = np.zeros_like(src, dtype=float)

        for i in range(length, len(src)):
            tr_values = np.array([
                src.iloc[i] - src.iloc[i - 1],
                np.abs(src.iloc[i] - src.iloc[i - 1]),
                np.abs(src.iloc[i] - src.iloc[i - length])
            ])
            atr_values[i] = np.mean(tr_values) * mult

        up = hl2 + atr_values
        dn = hl2 - atr_values

        upper = lower = 0.0

        upper = np.where(src < upper, np.minimum(up, upper), up)
        lower = np.where(src > lower, np.maximum(dn, lower), dn)

        os, max_val, min_val = 0, src.iloc[0], src.iloc[0]

        os = np.where(src > upper, 1, np.where(src < lower, 0, os))
        spt = np.where(os == 1, lower, upper)

        shifted_max_val = np.roll(max_val, 1)

        max_val = np.where(
            np.where(src > spt, True, False),
            np.maximum(src, shifted_max_val),
            np.where(
                os == 1,
                np.maximum(src, shifted_max_val),
                spt
            )
        )

        shifted_min_val = np.roll(min_val, 1)

        min_val = np.where(
            np.where(src > spt, True, False),
            np.minimum(src, shifted_min_val),
            np.where(
                os == 0,
                np.minimum(src, shifted_min_val),
                spt
            )
        )
        return np.nanmean([max_val, min_val], axis=0)

    @staticmethod
    def avgX(src, high, low, length, mult):
        hl2 = (high + low) / 2

        atr_values = np.zeros_like(src, dtype=float)

        for i in range(length, len(src)):
            tr_values = np.array([
                src.iloc[i] - src.iloc[i - 1],
                np.abs(src.iloc[i] - src.iloc[i - 1]),
                np.abs(src.iloc[i] - src.iloc[i - length])
            ])
            atr_values[i] = np.mean(tr_values) * mult

        up = hl2 + atr_values
        dn = hl2 - atr_values

        # Initialize Series with zeros
        os = pd.Series(0, index=src.index)
        max_val = pd.Series(0, index=src.index)
        min_val = pd.Series(0, index=src.index)

        # Calculate os based on conditions
        os = np.where(src > up, 1, np.where(src < dn, 0, os))

        # Calculate spt using pandas Series
        spt = pd.Series(np.where(os == 1, dn, up), index=src.index)

        # Calculate max_val and min_val based on ta_cross condition
        max_val = np.where(IndHelper.ta_cross(src, spt), np.maximum(src, max_val), spt)
        min_val = np.where(IndHelper.ta_cross(src, spt), np.minimum(src, min_val), spt)

        return (max_val + min_val) / 2

    @staticmethod
    def ta_cross(a, b):
        return np.logical_and(a > b, a.shift(1) <= b.shift(1))
