from Indicator import Indicator
from datetime import datetime
from Util import logger
import pandas as pd

from Util import getISTTimeNow
from TelgramCom import TemBot


class Trade:
    startTime = datetime(year=1, month=1, day=1, hour=0, minute=0, second=0)
    endTime = datetime(year=1, month=1, day=1, hour=0, minute=0, second=0)
    entry = -1.0
    exit = -1.0
    pnl = 0.0

    iSL = -1.0
    iSLStatus = 'Not set'
    orgStopLoss = -1.0
    trailingSL = -1.0
    pivotTarget = -1.0
    triggerEntryPrice = -1.0
    allTargets = []
    targetHitCount = 0
    targetHitPrice = -1
    rr12 = -1.0
    rr13 = -1.0
    rr14 = -1.0
    tradeOn = False
    buySell = 'WAIT'

    tradeStatus = 'Not Triggered'

    def __init__(self):
        self.reset()

    def reset(self):
        self.startTime = datetime(year=1, month=1, day=1, hour=0, minute=0, second=0)
        self.endTime = datetime(year=1, month=1, day=1, hour=0, minute=0, second=0)
        self.entry = -1.0
        self.exit = -1.0
        self.pnl = 0.0

        self.iSL = -1.0
        self.iSLStatus = 'Not set'
        self.orgStopLoss = -1.0
        self.trailingSL = -1.0
        self.pivotTarget = -1.0
        self.triggerEntryPrice = -1.0
        self.allTargets = []

        self.targetHitCount = 0
        self.targetHitPrice = -1

        self.rr12 = -1.0
        self.rr13 = -1.0
        self.rr14 = -1.0
        self.buySell = 'WAIT'
        self.tradeStatus = 'Not Triggered'


class TradeTrigger:
    Trade = Trade()
    TradeInd = Indicator()
    columns = ['start', 'end', 'trigger', 'exit', 'pnl', 'status', 'ON', 'type',
               'iSLStatus', 'entry', 'orgSL', 'trailingSL', 'iSL', 'currentTarget',
               'allTargets', 'targetHitCount', 'targetHitPrice']

    tradeBook = pd.DataFrame(columns=columns)
    bot = TemBot()

    def __init__(self):

        self.Trade = Trade()

    def reset(self):
        self.Trade = Trade()

    def execute(self, ind):

        if not self.Trade.tradeOn:
            self.TradeInd = ind
            self.reset()

            self.setEntryAndSL()
            self.setTarget()
            self.isTradeTriggered()
            self.printTrade()

        else:
            self.monitorTrade()

    def monitorTrade(self):
        self.isStopLossHit()
        self.isTargetHit()
        self.printTrade()

    def printTrade(self):

        message = "-------------------------------------"

        message = f"{message}\n Trade On: {self.Trade.tradeOn}"

        message = f"{message}\n Trade start: {self.Trade.startTime}, Trade end: {self.Trade.endTime}"
        message = f"{message}\n Trigger Price: {self.Trade.triggerEntryPrice}, Exit: {self.Trade.exit} PNL: {self.Trade.pnl}"
        message = f"{message}\n Type: {self.Trade.buySell}, Trade status: {self.Trade.tradeStatus}, iSL status: {self.Trade.iSLStatus}"
        message = f"{message}\n Entry: {self.Trade.entry}, Pivot Dynamic Target: {self.Trade.pivotTarget}"

        message = f"{message}\n OrgSL: {self.Trade.orgStopLoss}, Trailing-SL: {self.Trade.trailingSL} i-SL: {self.Trade.iSL}"

        message = f"{message}\n Target Hit Count: {self.Trade.targetHitCount}"
        message = f"{message}\n Target Hit Price: {self.Trade.targetHitPrice}"
        message = f"{message}\n Current Target: {self.Trade.pivotTarget}"

        for count, value in enumerate(self.Trade.allTargets, start=1):
            message += f"Target{count}: {value} "

        message = f"{message}\n-------------------------------------"

        logger.info(message)
        self.bot.sendMessage(message)

    def recordTrade(self):

        targetStr = ''
        for count, value in enumerate(self.Trade.allTargets, start=1):
            targetStr += f"Target{count}: {value} "

        new_row1 = {'start': self.Trade.startTime, 'end': self.Trade.endTime,
                    'trigger': self.Trade.triggerEntryPrice,
                    'exit': self.Trade.exit, 'pnl': self.Trade.pnl,
                    'status': self.Trade.tradeStatus, 'ON': self.Trade.tradeOn, 'type': self.Trade.buySell,
                    'iSLStatus': self.Trade.iSLStatus, 'entry': self.Trade.entry, 'orgSL': self.Trade.orgStopLoss,
                    'trailingSL': self.Trade.trailingSL, 'iSL': self.Trade.iSL,
                    'currentTarget': self.Trade.pivotTarget, 'allTargets': targetStr,
                    'targetHitCount': self.Trade.targetHitCount, 'targetHitPrice': self.Trade.targetHitPrice}
        self.tradeBook.loc[len(self.tradeBook)] = new_row1

        logger.info("TradeBook Start")
        for index, record in self.tradeBook.iterrows():
            logger.info(
                f"Trade#: {index}\n ON: {record['ON']} Status: {record['status']} iSL Status: {record['iSLStatus']} Type: {record['type']} "
                f"\nStart Time: {record['start']} End Time:{record['end']}"
                f"\nEntry Price: {record['trigger']} Exit Price: {record['exit']} PNL:{record['pnl']}"
                f"\nEntry Price: {record['entry']} ORG SL: {record['orgSL']} Trailing SL:{record['trailingSL']} "
                f"\niSL:{record['iSL']} Current Target: {record['currentTarget']}"
                f"\nTargetHitcount: {record['targetHitCount']} TargetHitprice: {record['targetHitPrice']}  "
                f"\nAll Targets: {record['allTargets']}")

        logger.info("TradeBook End")

        self.tradeBook.to_csv('tradebook.csv', header=True, index=True)

    # this function will decide the entry point

    def setEntryAndSL(self):
        # get last candle for the 5 min with IRB buy or sell
        time5 = '5m'
        data5 = self.TradeInd.newSignalData[time5].data
        data5 = data5.reset_index()
        last_result = self.TradeInd.rData.iloc[-1]['result'] if len(self.TradeInd.rData) else ''

        last_result = last_result.lower()
        if 'buy' in last_result:
            self.setBuyTrade()

        if 'sell' in last_result:
            self.setSellTrade()

    def setBuyTrade(self):
        # get last candle for the 5 min with IRB buy or sell
        self.Trade.buySell = 'BUY'
        high, low = self.getPreviousIRB(lookBack=2, tsl=True)

        if high != 0:
            self.Trade.entry = high
            self.Trade.orgStopLoss = self.Trade.trailingSL = self.Trade.iSL = round(low)

    def setSellTrade(self):
        # get last candle for the 5 min with IRB buy or sell
        self.Trade.buySell = 'SELL'
        high, low = self.getPreviousIRB(lookBack=2, tsl=True)
        if high != 0:
            self.Trade.entry = low
            self.Trade.orgStopLoss = self.Trade.trailingSL = self.Trade.iSL = round(high)

    # this function will decide the target point
    def setTarget(self):
        time5 = '5m'
        data5 = self.TradeInd.newSignalData[time5].data
        data5 = data5.reset_index()

        last_result = self.TradeInd.rData.iloc[-1]['result'] if len(self.TradeInd.rData) else ''

        close = data5.iloc[-2]['Close']

        high, low = self.getPreviousIRB(lookBack=2)

        last_result = last_result.lower()
        if 'buy' in last_result and high != 0:
            self.setTargetBuy(close=close)

        if 'sell' in last_result and high != 0:
            self.setTargetSell(close=close)

    def setTargetBuy(self, close):

        roomLength = self.Trade.entry - self.Trade.orgStopLoss
        self.Trade.rr12 = round(self.Trade.entry + 2 * roomLength, 2)
        self.Trade.rr13 = round(self.Trade.entry + 3 * roomLength, 2)
        self.Trade.rr14 = round(self.Trade.entry + 4 * roomLength, 2)
        values = [self.TradeInd.r1, self.TradeInd.r2, self.TradeInd.r3, self.TradeInd.s1, self.TradeInd.s2,
                  self.TradeInd.s3, self.TradeInd.tHigh, self.TradeInd.tLow, self.TradeInd.phigh, self.TradeInd.plow,
                  self.TradeInd.pivot, self.Trade.rr12, self.Trade.rr13,
                  self.Trade.rr14, self.TradeInd.vwap, self.TradeInd.yvwap]

        filtered_values = [value for value in values if value > (close + roomLength)]

        # Sort the filtered values
        self.Trade.allTargets = sorted(filtered_values)

        if len(self.Trade.allTargets) > 0:
            self.Trade.pivotTarget = self.Trade.allTargets[0]

    def setTargetSell(self, close):
        roomLength = self.Trade.orgStopLoss - self.Trade.entry
        self.Trade.rr12 = round(self.Trade.entry - 2 * roomLength, 2)
        self.Trade.rr13 = round(self.Trade.entry - 3 * roomLength, 2)
        self.Trade.rr14 = round(self.Trade.entry - 4 * roomLength, 2)
        values = [self.TradeInd.r1, self.TradeInd.r2, self.TradeInd.r3, self.TradeInd.s1, self.TradeInd.s2,
                  self.TradeInd.s3, self.TradeInd.tHigh, self.TradeInd.tLow, self.TradeInd.phigh,
                  self.TradeInd.plow,
                  self.TradeInd.pivot, self.Trade.rr12, self.Trade.rr13,
                  self.Trade.rr14, self.TradeInd.vwap, self.TradeInd.yvwap]

        filtered_values = [value for value in values if ((close - roomLength) > value > 0)]

        # Sort the filtered values
        sorted_values = sorted(filtered_values, reverse=True)

        if len(self.Trade.allTargets) > 0:
            self.Trade.pivotTarget = self.Trade.allTargets[0]

    # trail the stoploss to logical point
    def trailStopLoss(self):
        # look for the last 5 min bar high/low based on buy sell
        time5 = '5m'
        data5 = self.TradeInd.newSignalData[time5].data
        data5 = data5.reset_index()

        high, low = self.getPreviousIRB(lookBack=2, tsl=True)

        last_result = self.TradeInd.rData.iloc[-1]['result'] if len(self.TradeInd.rData) else ''
        last_result = last_result.lower()
        if 'buy' in last_result and low != 0:
            self.Trade.trailingSL = low

        if 'sell' in last_result and high != 0:
            self.Trade.trailingSL = high

    def getPreviousIRB(self, sameDay=True, irb=True, lookBack=10, tsl=False):
        time5 = '5m'
        data5 = self.TradeInd.newSignalData[time5].data

        if not irb:
            low = data5.iloc[-2]['Low']
            high = data5.iloc[-2]['High']
        else:
            low = high = 0

        # Convert the index to DDMMYY format
        if sameDay:

            data5.index = pd.to_datetime(data5.index)

            # Find the index of the row with the latest date
            latest_date = data5.index[-1].date()

            # Filter the DataFrame based on the target date
            latest_date_records = data5[data5.index.date == latest_date]

            length = len(latest_date_records)
            count = 1

            for i in range(length - 2, -1, -1):
                if count <= lookBack:
                    row = latest_date_records.iloc[i]
                    irbLong = row['IRBLONG']
                    irbShort = row['IRBSHORT']

                    if irbLong or irbShort:
                        if high == 0:
                            high = row['High']
                            low = row['Low']

                        if tsl and self.Trade.buySell == 'BUY':
                            high = min(high, row['High'])
                            low = min(low, row['Low'])
                        elif tsl and self.Trade.buySell == 'SELL':
                            high = max(high, row['High'])
                            low = max(low, row['Low'])
                        else:
                            break

                    count += 1
                else:
                    break

            # data5.index = data5.index.strftime('%Y-%m-%d %H:%M:%S')

        return high, low

    def modifyPivotTarget(self):

        values = []

        if self.Trade.buySell == 'BUY':
            values = [value for value in self.Trade.allTargets if value > self.Trade.pivotTarget]
        elif self.Trade.buySell == 'SELL':
            values = [value for value in self.Trade.allTargets if value < self.Trade.pivotTarget]

        if len(values) > 0:
            self.Trade.pivotTarget = values[0]
        else:
            self.Trade.tradeOn = False

    def handleTargetHit(self, close):
        self.Trade.exit = close
        self.Trade.tradeOn = True
        self.Trade.endTime = getISTTimeNow()
        self.Trade.targetHitPrice = self.Trade.pivotTarget
        self.Trade.targetHitCount += 1
        self.Trade.pnl += abs(self.Trade.exit - self.Trade.triggerEntryPrice)

        self.recordTrade()

        self.trailStopLoss()
        self.modifyPivotTarget()

        # this function will decide if the target is hit

    def isTargetHit(self):
        if self.Trade.tradeOn:
            time1 = '1m'
            data1 = self.TradeInd.newSignalData[time1].data
            data1 = data1.reset_index()
            close = data1.iloc[-2]['Close']
            if (self.Trade.buySell == 'BUY') and (close > self.Trade.pivotTarget):
                self.handleTargetHit(close)
            else:
                self.checkTrailingPossible(close)

            if (self.Trade.buySell == 'SELL') and (close < self.Trade.pivotTarget):
                self.handleTargetHit(close)
            else:
                self.checkTrailingPossible(close)

    def checkTrailingPossible(self, min1Close):
        # if moving towards target 50% then move SL to entry if moved close to target 80% then move SL to 50%
        # this will ensure the intermediate profit booking
        # taking reference of Current Target for setting the iSL
        # If the iSL is set then only Trail the SL

        self.trailISL(min1Close)
        if self.Trade.iSLStatus != 'Not set':
            self.trailStopLoss()

    def trailISL(self, min1Close):

        if self.Trade.buySell == 'BUY':
            diff = abs(self.Trade.pivotTarget - self.Trade.triggerEntryPrice)
            halfWay = self.Trade.triggerEntryPrice + (diff * 0.5)
            eightyPer = self.Trade.triggerEntryPrice + (diff * 0.8)

            if min1Close > halfWay:
                self.Trade.iSL = self.Trade.triggerEntryPrice
                self.Trade.iSLStatus = 'Moved to Entry zero loss'
            if min1Close > eightyPer:
                self.Trade.iSL = halfWay
                self.Trade.iSLStatus = 'Moved to 50% ensure half'

        elif self.Trade.buySell == 'SELL':
            diff = abs(self.Trade.pivotTarget - self.Trade.triggerEntryPrice)
            halfWay = self.Trade.triggerEntryPrice - (diff * 0.5)
            eightyPer = self.Trade.triggerEntryPrice - (diff * 0.8)

            if min1Close > halfWay:
                self.Trade.iSL = self.Trade.triggerEntryPrice
                self.Trade.iSLStatus = 'Moved to Entry zero loss'
            if min1Close > eightyPer:
                self.Trade.iSL = halfWay
                self.Trade.iSLStatus = 'Moved to 50% ensure half'

    def isTradeTriggered(self):
        # here we will check if the trade is triggered based on the entry criteria
        # Check that 5 min close is above high for buy and 5 min close below low for sell
        triggered = False
        if self.Trade.entry > 0 and self.Trade.orgStopLoss > 0:
            time5 = '5m'
            data5 = self.TradeInd.newSignalData[time5].data
            data5 = data5.reset_index()
            if self.normalCandle(data5.iloc[-2]['High'], data5.iloc[-2]['Low'], data5.iloc[-2]['Close']):

                if (self.Trade.buySell == 'BUY') and (data5.iloc[-2]['Close'] > self.Trade.entry):
                    triggered = True

            if (self.Trade.buySell == 'SELL') and (data5.iloc[-2]['Close'] < self.Trade.entry):
                triggered = True

            if triggered:
                self.Trade.tradeOn = True
                time1 = '1m'
                data1 = self.TradeInd.newSignalData[time1].data
                data1 = data1.reset_index()

                self.Trade.triggerEntryPrice = data1.iloc[-2]['Close']
                self.Trade.startTime = getISTTimeNow()
                self.Trade.tradeStatus = 'Triggered'

        return triggered

    def normalCandle(self, high, low, close):
        stat = False
        triggerCandleSpan = round(high - low, 2)
        length = 70
        entryCandleSpan = abs(self.Trade.entry - self.Trade.orgStopLoss)
        entryCandleSpan = round(entryCandleSpan, 2)

        limit = self.Trade.entry
        if self.Trade.buySell == 'BUY':
            limit = self.Trade.entry + entryCandleSpan
            if close < limit:
                stat = True
            else:
                logger.info(f"Close: {close} Limit: {limit} "
                            f"\n RULE1: For Buy Close < Limit is not satisfied")

        if self.Trade.buySell == 'SELL':
            limit = self.Trade.entry - entryCandleSpan
            if close > limit:
                stat = True
            else:
                stat = False
                logger.info(f"Close: {close} Limit: {limit} "
                            f"\n RULE1: For SELL Close > Limit is not satisfied")

        if triggerCandleSpan < 2 * entryCandleSpan and entryCandleSpan < length:
            if stat: #Checking earlier status is true and then only setting as true
                stat = True
            else:
                stat = False
                logger.info("Candle length condition is OK but Candle close condition is not satisfied")
        else:
            logger.info(f"EntryCandleSpan: {entryCandleSpan} Trigger span: {triggerCandleSpan} "
                    f"\n RULE2:Trigger candle span < {2 * entryCandleSpan} and Entry candle span < {length} ")
            stat = False

        return stat

    def handleSLHit(self, close, trailing=False, iSL=False):
        self.Trade.exit = close
        self.Trade.endTime = getISTTimeNow()
        self.Trade.tradeOn = False
        self.Trade.pnl = self.Trade.exit - self.Trade.triggerEntryPrice

        if self.Trade.buySell == 'SELL':
            self.Trade.pnl = self.Trade.triggerEntryPrice - self.Trade.exit

        self.Trade.pnl = round(self.Trade.pnl, 2)

        self.Trade.tradeStatus = f"Original SL hit for {self.Trade.buySell}"

        if trailing:
            self.Trade.tradeStatus = f"Trailing SL hit for {self.Trade.buySell}"

        if iSL:
            self.Trade.tradeStatus = f"Intelligent SL hit for {self.Trade.buySell}"

        self.recordTrade()

    # this function will decide if the stoploss/trailing stoploss is hit
    def isStopLossHit(self):
        if self.Trade.tradeOn:
            if self.Trade.buySell == 'BUY':
                self.checkSLForBuy()
            elif self.Trade.buySell == 'SELL':
                self.checkSLForSell()

    def checkSLForBuy(self):
        time5 = '5m'
        data5 = self.TradeInd.newSignalData[time5].data
        data5 = data5.reset_index()
        close = data5.iloc[-2]['Close']
        # Check the difference is atlest greater than 1
        if close < self.Trade.orgStopLoss and (self.Trade.orgStopLoss - close) > 1:
            self.handleSLHit(close)

        elif close < self.Trade.trailingSL and (self.Trade.trailingSL - close) > 1:
            if self.Trade.trailingSL != self.Trade.orgStopLoss:
                self.handleSLHit(close, trailing=True)

        elif close < self.Trade.iSL and (self.Trade.iSL - close) > 1:
            if self.Trade.iSL != self.Trade.orgStopLoss:
                self.handleSLHit(close, iSL=True)

    def checkSLForSell(self):
        time5 = '5m'
        data5 = self.TradeInd.newSignalData[time5].data
        data5 = data5.reset_index()
        close = data5.iloc[-2]['Close']

        if close > self.Trade.orgStopLoss and (close - self.Trade.orgStopLoss) > 1:
            self.handleSLHit(close)

        # Check the difference is atlest greater than 1
        elif close > self.Trade.trailingSL and (close - self.Trade.trailingSL) > 1:
            if self.Trade.trailingSL != self.Trade.orgStopLoss:
                self.handleSLHit(close, trailing=True)

        elif close > self.Trade.iSL and (close - self.Trade.iSL) > 1:
            if self.Trade.iSL != self.Trade.orgStopLoss:
                self.handleSLHit(close, iSL=True)

    def runTrade(self):
        pass

    def forceExit(self):
        pass

    def exit(self):
        pass
