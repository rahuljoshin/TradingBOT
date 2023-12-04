import yfinance as yf
import pandas as pd

from datetime import date
from datetime import timedelta

class BankniftyCls:
    banknifty_Stocks = ["BANDHANBNK.NS", "RBLBANK.NS", "BANKBARODA.NS", "PNB.NS", "ICICIBANK.NS", "SBIN.NS",
                        "IDFCFIRSTB.NS", "AXISBANK.NS", "INDUSINDBK.NS", "HDFCBANK.NS", "KOTAKBANK.NS", "AUBANK.NS"]

    bn_ticker = '^NSEBANK'

    def get_BNData(self, interval='5m', period='1d', start=None, end=None):

        bnData = pd.DataFrame()
        df = pd.DataFrame()

        if start is None:
            bnData = yf.download(tickers=self.bn_ticker, interval=interval, period=period, start=start, end=end)
            df = yf.download(tickers=self.banknifty_Stocks, interval=interval, period=period, start=start, end=end)
        else:
            bnData = yf.download(tickers=self.bn_ticker, start=start, end=end,interval=interval)
            df = yf.download(tickers=self.banknifty_Stocks, start=start, end=end,interval=interval)

        substring = 'Volume'

        bnData['Volume'] = df[[col for col in df.columns if substring in col]].sum(axis=1)

        bnData.index = pd.to_datetime(bnData.index)

        # Calculate the cumulative sum of (price * volume) and volume
        bnData['Price'] = (bnData['High'] + bnData['Low']) / 2
        bnData['Price_times_Volume'] = bnData['Price'] * bnData['Volume']

        criteria = bnData.index.strftime('%Y-%m-%d')

        bnData['Cumulative_Price_Volume'] = bnData.groupby(criteria)[['Price_times_Volume']].cumsum()

        bnData['Cumulative_Volume'] = bnData.groupby(criteria)[['Volume']].cumsum()

        bnData['VWAP'] = bnData['Cumulative_Price_Volume'] / bnData['Cumulative_Volume']

        grouped = bnData.groupby(criteria)

        second_last_records = grouped.apply(lambda x: x.iloc[-1])

        second_last_records = second_last_records.reset_index()
        length = len(second_last_records) - 2

        if length >= 0:
            vwapLast = second_last_records.loc[length, 'VWAP']
            bnData['GOLDUP'], bnData['GOLD'], bnData['GOLDLOW'] = self.vwapGoldenLevels(vwapLast, bnData['VWAP'])
        else:
            bnData['GOLDUP'], bnData['GOLD'], bnData['GOLDLOW'] = '', '', ''

        bnData.index = bnData.index.strftime('%Y-%m-%d %H:%M:%S')

        bnData = bnData.round(2)
        return bnData

    @staticmethod
    def vwapGoldenLevels(yVWAP, VWAP):
        golden = (yVWAP + VWAP) / 2

        zonedev = abs(yVWAP - VWAP)

        zone = 0.1
        goldenUpper = golden + (zonedev * zone)

        goldenLower = golden - (zonedev * zone)

        golden = round(golden, 2)
        goldenUpper = round(goldenUpper, 2)
        goldenLower = round(goldenLower, 2)

        return goldenUpper, golden, goldenLower

    # This function will return the candle
    # look_back = Look back candle number from end, if you want the second last candle then look_back=2
    # latest = This is the bool and return the latest candle for the interval
    def get_Candle(self, interval='5m', period='1d', look_back=2, latest=True):
        bndata = yf.download(tickers=self.bn_ticker, interval=interval, period=period)
        if latest and len(bndata) > 0:
            bndata = bndata.tail(1)

        elif len(bndata) >= look_back:
            bndata = bndata.take([-look_back])

        # Create a list of sequential values for the index
        index_sequence = [i for i in range(1, len(bndata) + 1)]

        # Set the sequential index
        bndata.index = index_sequence
        #bndata.index = pd.to_datetime(bndata.index)
        #bndata.index = bndata.index.strftime('%Y-%m-%d %H:%M:%S')
        #bndata.index = bndata.reset_index()

        bndata = bndata.round(2)
        return bndata

    def getVWAP(self, start_date, end_date):

        dataYDay = self.get_BNData(start=start_date, end=end_date)

        yDayVWAP = dataYDay[['VWAP', 'Close', 'Volume']].tail(1)
        yDayVWAP = yDayVWAP.reset_index()
        assert(len(yDayVWAP))
        vwapLast = yDayVWAP.loc[0, 'VWAP']

        return vwapLast


    def calGoldenLevel(self, yVWAP, VWAP):
        golden = (yVWAP + VWAP) / 2

        zonedev = abs(yVWAP - VWAP)

        zone = 0.1
        goldenUpper = golden + (zonedev * zone)

        goldenLower = golden - (zonedev * zone)

        golden = round(golden, 2)
        goldenUpper = round(goldenUpper, 2)
        goldenLower = round(goldenLower, 2)

        goldenLevel = {'GoldenUpper': goldenUpper,
                       'Golden': golden,
                       'GoldenLower': goldenLower}

        return goldenLevel
