import yfinance as yf
import pandas as pd

from datetime import date
from datetime import timedelta


class BankniftyCls:
    banknifty_Stocks = ["BANDHANBNK.NS", "RBLBANK.NS", "BANKBARODA.NS", "PNB.NS", "ICICIBANK.NS", "SBIN.NS",
                        "IDFCFIRSTB.NS", "AXISBANK.NS", "INDUSINDBK.NS", "HDFCBANK.NS", "KOTAKBANK.NS", "AUBANK.NS"]

    bn_ticker = '^NSEBANK'

    def get_BNData(self, interval='5m', period='1d', start=None, end=None):

        if start is None:
            bnData = yf.download(tickers=self.bn_ticker, interval=interval, period=period, start=start, end=end)
            df = yf.download(tickers=self.banknifty_Stocks, interval=interval, period=period, start=start, end=end)
        else:
            bnData = yf.download(tickers=self.bn_ticker, start=start, end=end, interval=interval)
            df = yf.download(tickers=self.banknifty_Stocks, start=start, end=end, interval=interval)

        volume_columns = [col for col in df.columns if 'Volume' in col]
        collective_volume = df[volume_columns].sum(axis=1)

        # Align the indices of `bnData` and `collective_volume`
        collective_volume = collective_volume.reindex(bnData.index, method='nearest')

        # Add the collective volume as a new column to `bnData`
        bnData['Collective_Volume'] = collective_volume

        # Calculate the average of High and Low prices
        bnData['Avg_High_Low'] = (bnData['High'] + bnData['Low']) / 2

        # Calculate the price-volume product
        bnData['Price_Volume_Product'] = bnData['Avg_High_Low'] * bnData['Collective_Volume']

        # Group by each day to calculate daily VWAP
        bnData['Daily_Cumulative_Price_Volume'] = bnData.groupby(pd.Grouper(freq='D'))['Price_Volume_Product'].cumsum()
        bnData['Daily_Cumulative_Volume'] = bnData.groupby(pd.Grouper(freq='D'))['Collective_Volume'].cumsum()

        # Calculate the daily VWAP
        bnData['VWAP'] = bnData['Daily_Cumulative_Price_Volume'] / bnData['Daily_Cumulative_Volume']
        # Extract the last VWAP value for each day
        daily_vwap = bnData.groupby(bnData.index.date)['VWAP'].last()

        # Check if there are enough records to proceed
        if len(daily_vwap) > 1:
            vwapLast = daily_vwap.iloc[-2]
            # Assuming self.vwapGoldenLevels is defined elsewhere and returns three values
            bnData['GOLDUP'], bnData['GOLD'], bnData['GOLDLOW'] = self.vwapGoldenLevels(vwapLast, bnData['VWAP'])
        else:
            bnData['GOLDUP'], bnData['GOLD'], bnData['GOLDLOW'] = '', '', ''

        # Format the index and round values for final output
        #bnData.index = bnData.index.strftime('%Y-%m-%d %H:%M:%S')
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
        # bndata.index = pd.to_datetime(bndata.index)
        # bndata.index = bndata.index.strftime('%Y-%m-%d %H:%M:%S')
        # bndata.index = bndata.reset_index()

        bndata = bndata.round(2)
        return bndata

    def getVWAP(self, start_date, end_date):

        dataYDay = self.get_BNData(start=start_date, end=end_date)

        yDayVWAP = dataYDay[['VWAP', 'Close', 'Volume']].tail(1)
        yDayVWAP = yDayVWAP.reset_index()
        assert (len(yDayVWAP))
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
