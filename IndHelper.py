import numpy as np
import pandas as pd
import pandas_ta as taL
import ta as lib
import ta.trend
from ta.trend import PSARIndicator
#import ta.volatility


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

        # sarValues = PSARIndicator(high=high.squeeze(), low=low.squeeze(),
        # close=close.squeeze()).psar()

        psar = taL.psar(high=high, low=low, close=close)

        sarValues = psar['PSARl_0.02_0.2'].fillna(psar['PSARs_0.02_0.2'])
        return sarValues

    @staticmethod
    def getRSI(close, window=9):

        # rsiValues1 = lib.wrapper.RSIIndicator(close=close.squeeze(), window=window,fillna=True).rsi()
        rsiValues = taL.rsi(close=close, length=window)
        return rsiValues

    @staticmethod
    def getEMA(close, window=9):

        # emaValues = lib.wrapper.EMAIndicator(close=close.squeeze(), window=window, fillna=True).ema_indicator()
        emaValues = taL.ema(close=close, length=window)
        return emaValues

    @staticmethod
    def calculateKeltnerChannel(high, low, close, period=20, multiplier=1.5):
        # Calculate True Range (TR)

        # Calculate the Exponential Moving Average (EMA)
        # ema = close.ewm(span=period, adjust=False).mean()

        # ema = pandaTa.ema(close=close, length=period)

        # Calculate the Average True Range (ATR)
        kc = taL.kc(high=high, low=low, close=close, length=period, scalar=multiplier)
        return kc.iloc[:, 0], kc.iloc[:, 1], kc.iloc[:, 2]
        # return kc[]

        # atr = ta.volatility.AverageTrueRange(high=high, low=low, close=close,
        # window=period).average_true_range()

        # Calculate the Keltner Channel Bands
        # kUpperBand = ema + (atr * multiplier)
        # kLowerBand = ema - (atr * multiplier)

        # return kUpperBand, ema, kLowerBand

    import pandas as pd
    import numpy as np
    @staticmethod
    def lux_super_ichi(df, tenkan_len=9, tenkan_mult=2.0, kijun_len=26, kijun_mult=4.0,
                       spanB_len=52, spanB_mult=6.0, offset=26):

        def calculate_avg(src, length, mult):
            # 1. Calculate ATR
            tr = pd.concat([
                (df['High'] - df['Low']),
                (df['High'] - df['Close'].shift(1)).abs(),
                (df['Low'] - df['Close'].shift(1)).abs()
            ], axis=1).max(axis=1)
            atr = tr.rolling(window=length).mean() * mult

            hl2 = (df['High'] + df['Low']) / 2
            up = hl2 + atr
            dn = hl2 - atr

            upper = np.zeros(len(df))
            lower = np.zeros(len(df))
            os = np.zeros(len(df))
            spt = np.zeros(len(df))
            max_val = np.zeros(len(df))
            min_val = np.zeros(len(df))

            # Recursive calculation
            for i in range(1, len(df)):
                # Use .iloc[i] for current position and .iloc[i-1] for previous position
                prev_src = src.iloc[i - 1]
                prev_upper = upper[i - 1]
                prev_lower = lower[i - 1]

                # Upper/Lower trailing bands
                upper[i] = min(up.iloc[i], prev_upper) if prev_src < prev_upper else up.iloc[i]
                lower[i] = max(dn.iloc[i], prev_lower) if prev_src > prev_lower else dn.iloc[i]

                # Trend Direction (os)
                os[i] = 1 if src.iloc[i] > upper[i] else (0 if src.iloc[i] < lower[i] else os[i - 1])

                # Support/Resistance Point (spt)
                spt[i] = lower[i] if os[i] == 1 else upper[i]

                # Detect Cross
                prev_spt = spt[i - 1]
                curr_src = src.iloc[i]
                cross = (curr_src > spt[i] and prev_src <= prev_spt) or (curr_src < spt[i] and prev_src >= prev_spt)

                # Max/Min calculation
                if cross or os[i] == 1:
                    max_val[i] = max(curr_src, max_val[i - 1]) if not cross else curr_src
                else:
                    max_val[i] = spt[i]

                if cross or os[i] == 0:
                    min_val[i] = min(curr_src, min_val[i - 1]) if not cross else curr_src
                else:
                    min_val[i] = spt[i]

            return (max_val + min_val) / 2

        # Calculate Components
        df['tenkan'] = calculate_avg(df['Close'], tenkan_len, tenkan_mult)
        df['kijun'] = calculate_avg(df['Close'], kijun_len, kijun_mult)

        # Senkou Span A is the average of Tenkan and Kijun
        df['senkouA'] = (df['tenkan'] + df['kijun']) / 2

        # Senkou Span B uses the third set of inputs
        df['senkouB'] = calculate_avg(df['Close'], spanB_len, spanB_mult)

        # Shift Spans forward (Offset)
        df['senkouA_lead'] = df['senkouA'].shift(offset - 1)
        df['senkouB_lead'] = df['senkouB'].shift(offset - 1)

        return df
    @staticmethod
    def calculate_super_ichi(df, tenkan_len=9, kijun_len=26, senkou_len=52, atr_len=10, factor=3.0):
        """
        Calculates Super Ichi components.
        Note: Standard Ichimoku uses High/Low averages.
        Super Ichi enhances this by incorporating ATR-based volatility.
        """

        # 1. Calculate Standard Ichimoku components using pandas_ta
        ichi = taL.ichimoku(high=df['High'],close=df['Close'], low= df['Low'], tenkan=tenkan_len, kijun=kijun_len, senkou=senkou_len)[0]

        # 2. Calculate ATR for the volatility 'Super' component
        df['atr'] = taL.atr(df['High'], df['Low'], df['Close'], length=atr_len)

        # 3. Merge Ichimoku lines into our main dataframe
        df['tenkan'] = ichi[f'ITS_{tenkan_len}']
        df['kijun'] = ichi[f'IKS_{kijun_len}']
        df['span_a'] = ichi[f'ISA_{tenkan_len}']
        df['span_b'] = ichi[f'ISB_{kijun_len}']

        # 4. Apply Volatility Factor to smooth/filter (The "Super" Logic)
        # We adjust the Kumo Cloud boundaries based on ATR to reduce whipsaws
        df['super_span_a'] = df['span_a'] + (df['atr'] * factor * 0.1)
        df['super_span_b'] = df['span_b'] - (df['atr'] * factor * 0.1)

        # 5. Define Trend Logic
        # Bullish: Price > Span A and Span B
        # Bearish: Price < Span A and Span B
        df['trend'] = 0
        df.loc[(df['Close'] > df['super_span_a']) & (df['Close'] > df['super_span_b']), 'trend'] = 1
        df.loc[(df['Close'] < df['super_span_a']) & (df['Close'] < df['super_span_b']), 'trend'] = -1

        return df

    # Example Usage with dummy data
    # df = pd.read_csv('your_nifty_data.csv')
    # super_ichi_df = calculate_super_ichi(df)

    @staticmethod
    def newSuperIchi(data, tenkan_len=9, tenkan_mult=2.0, kijun_len=26, kijun_mult=4.0, spanB_len=52,
                     spanB_mult=6.0, offset=26):
        # Calculate basic ATR and HL2
        data['hl2'] = (data['High'] + data['Low']) / 2

        def calculate_custom_avg(src, length, mult):
            # Calculate ATR using pandas_ta or manual
            tr = pd.concat([data['High'] - data['Low'],
                            (data['High'] - src.shift(1)).abs(),
                            (data['Low'] - src.shift(1)).abs()], axis=1).max(axis=1)
            atr = tr.rolling(length).mean() * mult

            upper = np.zeros(len(data))
            lower = np.zeros(len(data))
            os = np.zeros(len(data))
            max_val = np.zeros(len(data))
            min_val = np.zeros(len(data))
            result = np.zeros(len(data))

            hl2 = data['hl2'].values
            src_val = src.values
            atr_val = atr.fillna(0).values

            for i in range(1, len(data)):
                up = hl2[i] + atr_val[i]
                dn = hl2[i] - atr_val[i]

                # Trailing Upper and Lower Bands
                upper[i] = min(up, upper[i - 1]) if src_val[i - 1] < upper[i - 1] else up
                lower[i] = max(dn, lower[i - 1]) if src_val[i - 1] > lower[i - 1] else dn

                # Trend Direction (os)
                if src_val[i] > upper[i]:
                    os[i] = 1
                elif src_val[i] < lower[i]:
                    os[i] = 0
                else:
                    os[i] = os[i - 1]

                spt = lower[i] if os[i] == 1 else upper[i]

                # Check for crossing (Source crossing the Support/Resistance Line)
                crossed = (src_val[i] > spt and src_val[i - 1] <= spt) or (
                        src_val[i] < spt and src_val[i - 1] >= spt)

                # Max/Min Logic
                if crossed:
                    max_val[i] = max(src_val[i], max_val[i - 1])
                    min_val[i] = min(src_val[i], min_val[i - 1])
                elif os[i] == 1:
                    max_val[i] = max(src_val[i], max_val[i - 1])
                    min_val[i] = min_val[i - 1]  # Carry forward
                else:
                    max_val[i] = spt
                    min_val[i] = min(src_val[i], min_val[i - 1])

                result[i] = (max_val[i] + min_val[i]) / 2

            return result

        # Calculate Tenkan and Kijun
        data['tenkan'] = calculate_custom_avg(data['Close'], tenkan_len, tenkan_mult)
        data['kijun'] = calculate_custom_avg(data['Close'], kijun_len, kijun_mult)

        # Senkou Span A (shifted forward)
        data['senkouA'] = ((data['tenkan'] + data['kijun']) / 2).shift(offset - 1)

        # Senkou Span B (shifted forward)
        data['senkouB'] = pd.Series(calculate_custom_avg(data['Close'], spanB_len, spanB_mult)).shift(offset - 1)

        return data

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
