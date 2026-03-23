import yfinance as yf
import pandas as pd

from datetime import date
from datetime import timedelta


class DataCollectorCls:
    banknifty_Stocks = ["BANDHANBNK.NS", "RBLBANK.NS", "BANKBARODA.NS", "PNB.NS", "ICICIBANK.NS", "SBIN.NS",
                        "IDFCFIRSTB.NS", "AXISBANK.NS", "INDUSINDBK.NS", "HDFCBANK.NS", "KOTAKBANK.NS", "AUBANK.NS"
                        ]

    bn_ticker = '^NSEBANK'

    nifty_Stocks = ["ADANIENT.NS", "ADANIPORTS.NS", "APOLLOHOSP.NS", "ASIANPAINT.NS", "AXISBANK.NS",
                        "BAJAJ-AUTO.NS", "BAJFINANCE.NS", "BAJAJFINSV.NS", "BEL.NS", "BHARTIARTL.NS",
                        "BPCL.NS", "BRITANNIA.NS", "CIPLA.NS", "COALINDIA.NS", "DIVISLAB.NS",
                        "DRREDDY.NS", "EICHERMOT.NS", "ETERNAL.NS", "GRASIM.NS", "HCLTECH.NS",
                        "HDFCBANK.NS", "HDFCLIFE.NS", "HEROMOTOCO.NS", "HINDALCO.NS", "HINDUNILVR.NS",
                        "ICICIBANK.NS", "INDIGO.NS", "INDUSINDBK.NS", "INFY.NS", "ITC.NS",
                        "JIOFIN.NS", "JSWSTEEL.NS", "KOTAKBANK.NS", "LTM.NS", "LT.NS",
                        "M&M.NS", "MARUTI.NS", "NESTLEIND.NS", "NTPC.NS", "ONGC.NS",
                        "POWERGRID.NS", "RELIANCE.NS", "SBILIFE.NS", "SBIN.NS", "SUNPHARMA.NS",
                        "TATACONSUM.NS", "TMCV.NS", "TATASTEEL.NS", "TCS.NS", "TECHM.NS",
                        "TITAN.NS", "TMPV.NS", "TRENT.NS", "ULTRACEMCO.NS", "WIPRO.NS"
                    ]

    nifty_ticker = '^NSEI'

    sensex_Stocks = [
                        "ADANIPORTS.BO", "ASIANPAINT.BO", "AXISBANK.BO", "BAJAJ-AUTO.BO", "BAJFINANCE.BO",
                        "BAJAJFINSV.BO", "BHARTIARTL.BO", "ETERNAL.BO", "HCLTECH.BO", "HDFCBANK.BO",
                        "HINDUNILVR.BO", "ICICIBANK.BO", "INDUSINDBK.BO", "INFY.BO", "ITC.BO",
                        "JSWSTEEL.BO", "KOTAKBANK.BO", "LT.BO", "M&M.BO", "MARUTI.BO",
                        "NESTLEIND.BO", "NTPC.BO", "POWERGRID.BO", "RELIANCE.BO", "SBIN.BO",
                        "SUNPHARMA.BO", "TATASTEEL.BO", "TCS.BO", "TECHM.BO", "TITAN.BO",
                        "ULTRACEMCO.BO"
                    ]

    sensex_ticker = '^BSESN'

    #ticker = bn_ticker
    stocks = banknifty_Stocks

    def __init__(self, market_type="BANKNIFTY"):
        self.market_type = market_type.upper()

        # Assign Index Ticker and Suffix based on type
        if self.market_type == "NIFTY":
            self.index_ticker = "^NSEI"
            self.stocks = self.nifty_Stocks

        elif self.market_type == "SENSEX":
            self.index_ticker = "^BSESN"
            self.stocks = self.sensex_Stocks

        if self.market_type == "BANKNIFTY":
            self.index_ticker = "^NSEBANK"
            self.stocks = self.banknifty_Stocks

    def get_Data(self, interval='5m', period='1d', start=None, end=None):

        if start is None:
            iData = yf.download(tickers=self.index_ticker, interval=interval, period=period, start=start, end=end)
            df = yf.download(tickers=self.stocks, interval=interval, period=period, start=start, end=end)
        else:
            iData = yf.download(tickers=self.index_ticker, start=start, end=end, interval=interval)
            df = yf.download(tickers=self.stocks, start=start, end=end, interval=interval)

        iData.columns = iData.columns.get_level_values(0)
        df.columns = df.columns.get_level_values(0)

        volume_columns = [col for col in df.columns if 'Volume' in col]
        collective_volume = df[volume_columns].sum(axis=1)

        # Align the indices of `iData` and `collective_volume`
        collective_volume = collective_volume.reindex(iData.index, method='nearest')

        # Add the collective volume as a new column to `iData`
        iData['Collective_Volume'] = collective_volume

        # Calculate the average of High and Low prices
        iData['Avg_High_Low'] = (iData['High'] + iData['Low']) / 2

        # Calculate the price-volume product
        iData['Price_Volume_Product'] = iData['Avg_High_Low'] * iData['Collective_Volume']

        # Group by each day to calculate daily VWAP
        iData['Daily_Cumulative_Price_Volume'] = iData.groupby(pd.Grouper(freq='D'))['Price_Volume_Product'].cumsum()
        iData['Daily_Cumulative_Volume'] = iData.groupby(pd.Grouper(freq='D'))['Collective_Volume'].cumsum()

        # Calculate the daily VWAP
        iData['VWAP'] = iData['Daily_Cumulative_Price_Volume'] / iData['Daily_Cumulative_Volume']
        # Extract the last VWAP value for each day
        daily_vwap = iData.groupby(iData.index.date)['VWAP'].last()

        # Check if there are enough records to proceed
        if len(daily_vwap) > 1:
            vwapLast = daily_vwap.iloc[-2]
            # Assuming self.vwapGoldenLevels is defined elsewhere and returns three values
            iData['GOLDUP'], iData['GOLD'], iData['GOLDLOW'] = self.vwapGoldenLevels(vwapLast, iData['VWAP'])
        else:
            iData['GOLDUP'], iData['GOLD'], iData['GOLDLOW'] = '', '', ''

        # Format the index and round values for final output
        #iData.index = iData.index.strftime('%Y-%m-%d %H:%M:%S')
        iData.index = pd.to_datetime(iData.index)
        # Check if the index is already timezone-aware
        if iData.index.tz is None:
            # Convert from UTC to IST (Indian Standard Time, UTC +5:30)
            iData.index = iData.index.tz_localize('UTC').tz_convert('Asia/Kolkata')
        else:
            # If already tz-aware, just convert it to IST
            iData.index = iData.index.tz_convert('Asia/Kolkata')

        iData = iData.round(2)
        return iData

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
        iData = yf.download(tickers=self.index_ticker, interval=interval, period=period)
        iData.columns = iData.columns.get_level_values(0)
        if latest and len(iData) > 0:
            iData = iData.tail(1)

        elif len(iData) >= look_back:
            iData = iData.take([-look_back])

        # Create a list of sequential values for the index
        index_sequence = [i for i in range(1, len(iData) + 1)]

        # Set the sequential index
        iData.index = index_sequence
        # iData.index = pd.to_datetime(iData.index)
        # iData.index = iData.index.strftime('%Y-%m-%d %H:%M:%S')
        # iData.index = iData.reset_index()

        iData = iData.round(2)
        return iData

    def getVWAP(self, start_date, end_date):

        dataYDay = self.get_Data(start=start_date, end=end_date)

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
