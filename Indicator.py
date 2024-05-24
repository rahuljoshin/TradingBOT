

from Banknifty import BankniftyCls

from TelgramCom import TemBot

from datetime import datetime
from datetime import timedelta


import heapq
from collections import namedtuple

from Util import logger
from Util import isWorkingHours

from Util import getISTTimeNow

from IndHelper import *


# from Derivatives import NSE


class Indicator:
    Signal = namedtuple('Signal', ['data', 'is_dirty'])

    # tradeTrigger = TradeTrigger()

    # All the data for timeframes
    newSignalData = {
        '1m': Signal(data=pd.DataFrame(), is_dirty=False),
        '5m': Signal(data=pd.DataFrame(), is_dirty=False),
        '15m': Signal(data=pd.DataFrame(), is_dirty=False),
        '30m': Signal(data=pd.DataFrame(), is_dirty=False),
        '1d': Signal(data=pd.DataFrame(), is_dirty=False)
    }

    TCPR = pivot = BCPR = s1 = s2 = s3 = r1 = r2 = r3 = phigh = plow = pclose = 0.0
    vwap = yvwap = 0.0

    tOpen = tHigh = tLow = tClose = 0.0

    # Top 3 price and volumes
    top_vol_records = []
    rData = pd.DataFrame()

    def __init__(self):
        self.reset()

    def reset(self):
        # [1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo]
        self.TCPR = self.pivot = self.BCPR = self.s1 = self.s2 = self.s3 = 0.0
        self.r1 = self.r2 = self.r3 = self.phigh = self.plow = self.pclose = 0.0

        self.vwap = self.yvwap = 0.0
        self.tOpen = self.tHigh = self.tLow = self.tClose = 0.0

        # Top 3 price and volumes
        self.top_vol_records = []

        # All the data for timeframes
        self.newSignalData = {
            '1m': self.Signal(data=pd.DataFrame(), is_dirty=False),
            '5m': self.Signal(data=pd.DataFrame(), is_dirty=False),
            '15m': self.Signal(data=pd.DataFrame(), is_dirty=False),
            '30m': self.Signal(data=pd.DataFrame(), is_dirty=False),
            '1d': self.Signal(data=pd.DataFrame(), is_dirty=False)
        }

        # self.derNse = NSE()
        # result data based on 5,30 mins data
        self.rData = pd.DataFrame()
        # tradeTrigger = TradeTrigger()

    def execute(self):
        self.calculatePivotLevels()
        self.todayOHLC()
        if self.allSignals():
            self.buyorSell()

        self.saveCSVs()

    def saveCSVs(self):
        try:
            # print('Signal CSV save started')
            logger.info('Signal CSV save started')
            self.rData.to_csv('0sign.csv', header=True, index=True)
            # print('Signal CSV save end')
            logger.info('Signal CSV save end')

            for key, value in self.newSignalData.items():
                if value.is_dirty:
                    message = f"{'Saving'} {str(key)} {'CSV started'}"
                    logger.info(message)
                    # print('Saving CSV', str(key), 'started')
                    data = value.data
                    self.newSignalData[key] = self.newSignalData[key]._replace(is_dirty=False)
                    # self.newSignalData[key].is_dirty = False

                    data.to_csv(f'{str(key)}.csv', header=True, index=True)

                    message = f"{'Saving'} {str(key)} {'CSV end'}"
                    logger.info(message)

        except (ConnectionResetError, ConnectionAbortedError) as e:
            logger.error("Error in CSV dump")

    def forceRecal(self, time='5m'):
        self.newSignalData[time] = self.newSignalData[time]._replace(is_dirty=True)

    def buyorSell(self):
        result = 'WAIT'
        # Logic for deciding buy or sell
        time30 = '30m'
        # data30 = self.signal_datas[time30]
        data30 = self.newSignalData[time30].data
        data30 = data30.reset_index()
        time5 = '5m'
        # data5 = self.signal_datas[time5]
        data5 = self.newSignalData[time5].data

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

        goldenBar = data5.iloc[-2]['GOLDBAR']
        vwapBar = data5.iloc[-2]['VWAPBAR']
        prevwapbar = data5.iloc[-2]['PVWAPBAR']

        pLowBar = data5.iloc[-2]['PRELOW']
        pHighBar = data5.iloc[-2]['PREHIGH']

        pivotBar = data5.iloc[-2]['PIVOT']

        r1Bar = data5.iloc[-2]['R1']
        r2Bar = data5.iloc[-2]['R2']
        r3Bar = data5.iloc[-2]['R3']

        s1Bar = data5.iloc[-2]['S1']
        s2Bar = data5.iloc[-2]['S2']
        s3Bar = data5.iloc[-2]['S3']

        top1VolBar = data5.iloc[-2]['TOP1VOL']
        top2VolBar = data5.iloc[-2]['TOP2VOL']
        top3VolBar = data5.iloc[-2]['TOP3VOL']

        if buy30min and buy5min:
            result = 'BESTBUY'
        elif sell30min and sell5min:
            result = 'BESTSELL'
        elif weakSell30min and sell5min:
            result = 'QUICKSELL'
        elif weakBuy30min and buy5min:
            result = 'QUICKBUY'

        if goldenBar:
            result = f"{result} {'*** 5MIN-GOLDBAR ***'}"
        if vwapBar:
            result = f"{result} {'*** 5MIN-VWAPBAR ***'}"
        if prevwapbar:
            result = f"{result} {'*** 5MIN-PRE-VWAPBAR ***'}"

        if pivotBar:
            result = f"{result} {'$$$ 5MIN-PIVOTBAR $$$'}"

        if r1Bar:
            result = f"{result} {'$$$ 5MIN-R1BAR $$$'}"
        if r2Bar:
            result = f"{result} {'$$$ 5MIN-R2BAR $$$'}"

        if r3Bar:
            result = f"{result} {'$$$ 5MIN-R3BAR $$$'}"

        if s1Bar:
            result = f"{result} {'$$$ 5MIN-S1BAR $$$'}"

        if s2Bar:
            result = f"{result} {'$$$5MIN-S2BAR $$$'}"

        if s3Bar:
            result = f"{result} {'$$$5MIN-S3BAR $$$'}"

        if pLowBar:
            result = f"{result} {'$$$5MIN-Previous LOWBAR $$$'}"

        if pHighBar:
            result = f"{result} {'$$$5MIN-Previous HighBAR $$$'}"

        if top1VolBar:
            result = f"{result} $$$Touching TOP1-{self.top_vol_records[0][0]}$$$"
        if top2VolBar:
            result = f"{result} $$$Touching TOP2-{self.top_vol_records[1][0]}$$$"
        if top3VolBar:
            result = f"{result} $$$Touching TOP3-{self.top_vol_records[2][0]}$$$"

        buySell5 = data5.iloc[-2]['BUYORSELL']
        buySell30 = data30.iloc[-2]['BUYORSELL']

        if buySell5 == buySell30 and buySell5 != 'WAIT':
            result = f"+++STRONG {buySell5} {result}+++"

        # goldZoneR = self.checkGoldZone()
        # result = f"{goldZoneR} {result}"

        last_result = self.rData.iloc[-1]['result'] if len(self.rData) else ''

        if result != last_result:
            new_row = {'result': result, 'time': getISTTimeNow()}

            # Create a new DataFrame with the new row
            new_df = pd.DataFrame(new_row, index=[0])

            # Concatenate the new DataFrame with the original DataFrame
            self.rData = pd.concat([self.rData, new_df], ignore_index=True)

            message = (f"Result {len(self.rData)} is: {self.rData.iloc[-1]['result']}"
                       f"from {self.rData.iloc[-1]['time']}")
            bot = TemBot()
            bot.sendMessage(message)
            logger.info(message)

        return result

    def checkGoldZone(self):
        result = ""
        time5 = '5m'
        # data5 = self.signal_datas[time5]
        data5 = self.newSignalData[time5].data

        data5 = data5.reset_index()
        inGoldZone = data5.iloc[-2]['INGOLDZ']
        vwapVal = data5.iloc[-2]['VWAP']
        goldVal = data5.iloc[-2]['GOLD']

        if vwapVal > goldVal and inGoldZone:
            result = "REBOUND BUY"

        if vwapVal < goldVal and inGoldZone:
            result = "REBOUND SELL"

        return result

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

    def getTopPriceVolumesforDay(self, num_levels=10):
        time5 = '5m'

        bank = BankniftyCls()
        data5 = bank.get_BNData(interval=time5, period='1d')

        price_data, volume_data = self.fixed_range_volume_profile(prices=data5['Close'], volumes=data5['Volume'],
                                                                  num_levels=num_levels)

        # Create a list of tuples containing price and volume data
        data = list(zip(price_data, volume_data))

        # Get the top 3 records based on the volume data in cloumn 1
        self.top_vol_records = heapq.nlargest(3, data, key=lambda x: x[1])

        for item in self.top_vol_records:
            message = f"Price: {item[0]} Volume:{item[1]}"
            logger.info(message)

        return self.top_vol_records

    def todayOHLC(self):
        bank = BankniftyCls()
        data = bank.get_Candle(period='1d', interval='1d', latest=True)
        self.tOpen = data.loc[1]['Open']
        self.tHigh = data.loc[1]['High']
        self.tLow = data.loc[1]['Low']
        self.tClose = data.loc[1]['Close']

        logger.info(f"\n Todays# Open:{self.tOpen} High:{self.tHigh} Low:{self.tLow} Close:{self.tClose}")

    def calculatePivotLevels(self):

        if self.TCPR == 0:
            logger.info("Calculating pivot level")
            bank = BankniftyCls()
            data = bank.get_Candle(period='5d', interval='1d', latest=False)
            self.phigh = data.loc[1]['High']
            self.plow = data.loc[1]['Low']
            self.pclose = data.loc[1]['Close']

            self.setFibPivotPoints()

            logger.info(f"TCPR: {self.TCPR} PIVOT: {self.pivot} BCPR: {self.BCPR}"
                        f"\nS1: {self.s1} S2: {self.s2} S3: {self.s3}"
                        f"\nR1: {self.r1} R2: {self.r2} R3: {self.r3}"
                        f"\nPHigh: {self.phigh} PLow: {self.plow} PClose: {self.pclose}")

            logger.info("Calculating pivot done")

    def setFibPivotPoints(self):
        self.pivot = round((self.phigh + self.plow + self.pclose) / 3, 2)
        self.BCPR = round((self.phigh + self.plow) / 2, 2)
        self.TCPR = round(self.pivot + (self.pivot - self.BCPR), 2)
        self.s1 = round(self.pivot - (0.382 * (self.phigh - self.plow)), 2)
        self.s2 = round(self.pivot - (0.618 * (self.phigh - self.plow)), 2)
        self.s3 = round(self.pivot - (1.0 * (self.phigh - self.plow)), 2)
        self.r1 = round(self.pivot + (0.382 * (self.phigh - self.plow)), 2)
        self.r2 = round(self.pivot + (0.618 * (self.phigh - self.plow)), 2)
        self.r3 = round(self.pivot + (1.0 * (self.phigh - self.plow)), 2)

    def allSignals(self):
        # count=1
        stat = False
        for key, value in self.newSignalData.items():
            if self.isRecalculate(str(key)):
                message = f"{'Find signals for'} {str(key)} {'started'}"
                logger.info(message)
                data = self.getSignals(interval=str(key))

                self.newSignalData[key] = self.newSignalData[key]._replace(data=data)
                self.newSignalData[key] = self.newSignalData[key]._replace(is_dirty=True)

                stat = True
                # data.to_csv(f'{str(key)}.csv', header=True, index=True)
                message = f"{'Find signals for'} {str(key)} {'end'}"
                logger.info(message)

        return stat

    def isRecalculate(self, ftime):
        stat = False
        # data = self.signal_datas[ftime]
        data = self.newSignalData[ftime].data
        if len(data):
            if self.newSignalData[ftime].is_dirty:
                stat = True
            if isWorkingHours():
                data.index = pd.to_datetime(data.index)
                timestamp = data.index[-1]
                datetime_object = datetime.utcfromtimestamp(timestamp.timestamp())

                current_time = getISTTimeNow()

                diff = current_time - datetime_object

                threshold_time_difference = timedelta()
                if ftime == '1m':
                    threshold_time_difference = timedelta(minutes=1)

                elif ftime == '5m':
                    threshold_time_difference = timedelta(minutes=5)
                elif ftime == '15m':
                    threshold_time_difference = timedelta(minutes=15)
                elif ftime == '30m':
                    threshold_time_difference = timedelta(minutes=30)
                elif ftime == '1d':
                    threshold_time_difference = timedelta(days=1)

                if diff > threshold_time_difference:
                    stat = True
        else:
            stat = True

        return stat

    def getSignals(self, interval='5m'):

        bank = BankniftyCls()
        bndata = pd.DataFrame()

        if interval == '1m' or interval == '5m':
            bndata = bank.get_BNData(interval=interval, period='5d')
        elif interval == '15m' or interval == '30m':
            bndata = bank.get_BNData(interval=interval, period='5d')
        elif interval == '1d':
            bndata = bank.get_BNData(interval=interval, period='1mo')

        # PSAR, RSI9,3,21 and stocastics
        bndata['SAR'] = lib.wrapper.PSARIndicator(high=bndata['High'], low=bndata['Low'], close=bndata['Close']).psar()

        bndata['RSI9'] = lib.wrapper.RSIIndicator(close=bndata['Close'], window=9).rsi()
        bndata['EMA3_RSI'] = lib.wrapper.EMAIndicator(bndata['RSI9'], window=3).ema_indicator()

        # Calculate VWMA with a period of 21 on RSI
        bndata['VWMA21_RSI'] = Indicator.vwma(bndata['RSI9'], bndata['Volume'], period=21)

        bndata['%K'], bndata['%D'] = IndHelper.getStoch(high=bndata['High'], low=bndata['Low'],
                                                        close=bndata['Close'], window=4, smooth_window=1)

        # SMA5,20,50 and EMA 18,50
        bndata['SMA5'] = bndata['Close'].rolling(window=5).mean()
        bndata['EMA18'] = bndata['Close'].ewm(span=18).mean()
        bndata['SMA20'] = bndata['Close'].rolling(window=20).mean()
        bndata['SMA50'] = bndata['Close'].rolling(window=50).mean()
        bndata['EMA50'] = bndata['Close'].ewm(span=50).mean()

        #bndata['SMA50'].fillna(bndata['EMA50'], inplace=True)
        bndata['SMA50'] = bndata['SMA50'].fillna(bndata['EMA50'])

        # Bollinger band 20,2
        bndata['BBUpperBand2'], bndata['BBLowerBand2'] = IndHelper.calBB(bndata['Close'], period=20, stddev=2)
        bndata['BBUpperBand1'], bndata['BBLowerBand1'] = IndHelper.calBB(bndata['Close'], period=20, stddev=1)

        bndata['kUpperBand'], bndata['kMiddleLine'], bndata['kLowerBand'] = (
            IndHelper.calculateKeltnerChannel(bndata['High'],
                                              bndata['Low'], bndata['Close'], period=20, multiplier=2))

        bndata['TTMSQ'] = (bndata['BBUpperBand2'] < bndata['kUpperBand']) & (
                bndata['BBLowerBand2'] > bndata['kLowerBand'])

        bndata['diff'] = bndata['Close'] - ((bndata['kMiddleLine'] + bndata['SMA20']) / 2)

        bndata['tenkan'], bndata['kijun'], bndata['senkouA'], bndata['senkouB'] = IndHelper.calcSuperIchi(
            bndata['Close'],
            bndata['High'],
            bndata['Low'])

        bndata['IRBLONG'], bndata['IRBSHORT'] = IndHelper.findIRB(bndata['Open'], bndata['High'], bndata['Low'],
                                                                  bndata['Close'])

        Indicator.findGoldVWAPBuySell(bndata)

        if interval == '5m' or interval == '15m':
            self.touchingIMPLevels(bndata)
            self.inTopVolumeZone(bndata)
            self.setVWAP(bndata)

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

        bndata = bndata.round(2)
        return bndata

    def inTopVolumeZone(self, bnData):
        self.getTopPriceVolumesforDay()

        # Check if the candle is crossing the top 3 volume price
        for i in range(len(self.top_vol_records)):
            item = self.top_vol_records[i]
            volPrice = item[0]
            column = f"TOP{i + 1}VOL"

            bnData[column] = (
                ((bnData['High'] > volPrice) & (bnData['Low'] < volPrice)
                 &
                 (bnData['IRBLONG'] | bnData['IRBSHORT'])
                 ))

    def touchingIMPLevels(self, bnData):

        self.calculatePivotLevels()

        bnData['PREHIGH'] = (
            ((bnData['High'] > self.phigh) & (bnData['Low'] < self.phigh)
             &
             (bnData['IRBLONG'] | bnData['IRBSHORT'])
             ))

        bnData['PRELOW'] = (
            ((bnData['High'] > self.plow) & (bnData['Low'] < self.plow)
             &
             (bnData['IRBLONG'] | bnData['IRBSHORT'])
             ))

        bnData['PIVOT'] = (
            ((bnData['High'] > self.pivot) & (bnData['Low'] < self.pivot)
             &
             (bnData['IRBLONG'] | bnData['IRBSHORT'])
             ))

        bnData['R1'] = (
            ((bnData['High'] > self.r1) & (bnData['Low'] < self.r1)
             &
             (bnData['IRBLONG'] | bnData['IRBSHORT'])
             ))

        bnData['R2'] = (
            ((bnData['High'] > self.r2) & (bnData['Low'] < self.r2)
             &
             (bnData['IRBLONG'] | bnData['IRBSHORT'])
             ))

        bnData['R3'] = (
            ((bnData['High'] > self.r3) & (bnData['Low'] < self.r3)
             &
             (bnData['IRBLONG'] | bnData['IRBSHORT'])
             ))

        bnData['S3'] = (
            ((bnData['High'] > self.s3) & (bnData['Low'] < self.s3)
             &
             (bnData['IRBLONG'] | bnData['IRBSHORT'])
             ))
        bnData['S2'] = (
            ((bnData['High'] > self.s2) & (bnData['Low'] < self.s2)
             &
             (bnData['IRBLONG'] | bnData['IRBSHORT'])
             ))

        bnData['S1'] = (
            ((bnData['High'] > self.s1) & (bnData['Low'] < self.s1)
             &
             (bnData['IRBLONG'] | bnData['IRBSHORT'])
             ))

        bnData['UpBB2IRB'] = (
            ((bnData['High'] > bnData['BBUpperBand2']) & (bnData['Low'] < bnData['BBUpperBand2'])
             &
             (bnData['IRBLONG'] | bnData['IRBSHORT'])
             ))

        bnData['LowBB2IRB'] = (
            ((bnData['High'] > bnData['BBLowerBand2']) & (bnData['Low'] < bnData['BBLowerBand2'])
             &
             (bnData['IRBLONG'] | bnData['IRBSHORT'])
             ))

        bnData['UpBB1IRB'] = (
            ((bnData['High'] > bnData['BBUpperBand1']) & (bnData['Low'] < bnData['BBUpperBand1'])
             &
             (bnData['IRBLONG'] | bnData['IRBSHORT'])
             ))

        bnData['LowBB1IRB'] = (
            ((bnData['High'] > bnData['BBLowerBand1']) & (bnData['Low'] < bnData['BBLowerBand1'])
             &
             (bnData['IRBLONG'] | bnData['IRBSHORT'])
             ))

        bnData['SMA5IRB'] = (
            ((bnData['High'] > bnData['SMA5']) & (bnData['Low'] < bnData['SMA5'])
             &
             (bnData['IRBLONG'] | bnData['IRBSHORT'])
             ))

    def setVWAP(self, bnData):
        self.vwap = bnData.iloc[-1]['VWAP']
        bnData.index = pd.to_datetime(bnData.index)
        criteria = bnData.index.strftime('%Y-%m-%d')
        grouped_data = bnData.groupby(criteria)

        # Get the second-to-last group
        second_last_group = list(grouped_data.groups.keys())[-2]

        # Access the last row of the second-to-last group
        second_last_group_last_row = grouped_data.get_group(second_last_group).iloc[-1]

        self.yvwap = second_last_group_last_row['VWAP']

    @staticmethod
    def findGoldVWAPBuySell(bndata):

        bndata['GOLDBAR'] = (

                    (((bndata['Low'] < bndata['GOLDUP']) &
                  (bndata['GOLDUP'] < bndata['High'])) & (bndata['IRBLONG'] | bndata['IRBSHORT'])) |
                (((bndata['Low'] < bndata['GOLD']) &
                  (bndata['GOLD'] < bndata['High'])) & (bndata['IRBLONG'] | bndata['IRBSHORT'])) |
                (((bndata['Low'] < bndata['GOLDLOW']) &
                  (bndata['GOLDLOW'] < bndata['High'])) &
                 (bndata['IRBLONG'] | bndata['IRBSHORT'])))

        bndata['INGOLDZ'] = (

                (((bndata['Low'] < bndata['GOLDUP']) &
                  (bndata['GOLDUP'] < bndata['High']))) |
                (((bndata['Low'] < bndata['GOLD']) &
                  (bndata['GOLD'] < bndata['High']))) |
                (((bndata['Low'] < bndata['GOLDLOW']) &
                  (bndata['GOLDLOW'] < bndata['High'])))
        )

        bndata['VWAPBAR'] = (((bndata['Low'] < bndata['VWAP']) & (bndata['VWAP'] < bndata['High']))
                             &
                             (bndata['IRBLONG'] | bndata['IRBSHORT'])
                             )

        bndata['PVWAPBAR'] = ((bndata['Low'] < ((2 * bndata['GOLD']) - bndata['VWAP'])) &
                              (((2 * bndata['GOLD']) - bndata['VWAP']) < bndata['High'])
                              &
                              (bndata['IRBLONG'] | bndata['IRBSHORT'])
                              )

    @staticmethod
    # Function to calculate VWMA
    def vwma(rsi9, volume, period=21):
        typical_price = rsi9
        TPV = typical_price * volume
        CumulativeTPV = TPV.rolling(window=period).sum()
        CumulativeVolume1 = volume.rolling(window=period).sum()
        VWMA21_RSI = CumulativeTPV / CumulativeVolume1
        return VWMA21_RSI
