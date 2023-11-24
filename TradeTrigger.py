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
    Target1 = -1.0
    Target2 = -1.0
    Target3 = -1.0
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
        self.Target1 = -1.0
        self.Target2 = -1.0
        self.Target3 = -1.0
        self.rr12 = -1.0
        self.rr13 = -1.0
        self.rr14 = -1.0
        self.buySell = 'WAIT'
        self.tradeStatus = 'Not Triggered'


class TradeTrigger:
    Trade = Trade()
    TradeInd = Indicator()
    columns = ['start', 'end', 'trigger', 'exit', 'pnl', 'status', 'ON', 'type',
               'iSLStatus', 'entry', 'orgSL', 'trailingSL', 'iSL', 'T1', 'T2', 'T3']

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
        message = f"{message}\n Target1: {self.Trade.Target1}, Target2: {self.Trade.Target2}, Target3: {self.Trade.Target3}"
        message = f"{message}\n-------------------------------------"

        logger.info(message)
        self.bot.sendMessage(message)

    def recordTrade(self):
        new_row1 = {'start': self.Trade.startTime, 'end': self.Trade.endTime,
                    'trigger': self.Trade.triggerEntryPrice,
                    'exit': self.Trade.exit, 'pnl': self.Trade.pnl,
                    'status': self.Trade.tradeStatus, 'ON': self.Trade.tradeOn, 'type': self.Trade.buySell,
                    'iSLStatus': self.Trade.iSLStatus, 'entry': self.Trade.entry, 'orgSL': self.Trade.orgStopLoss,
                    'trailingSL': self.Trade.trailingSL, 'iSL': self.Trade.iSL, 'T1': self.Trade.Target1,
                    'T2': self.Trade.Target2, 'T3': self.Trade.Target3}
        self.tradeBook.loc[len(self.tradeBook)] = new_row1

        logger.info("TradeBook Start")
        for index, record in self.tradeBook.iterrows():
            logger.info(
                f"Trade#: {index}\n ON: {record['ON']} Status: {record['status']} iSL Status: {record['iSLStatus']} Type: {record['type']} "
                f"\nStart Time: {record['start']} End Time:{record['end']}"
                f"\nEntry Price: {record['trigger']} Exit Price: {record['exit']} PNL:{record['pnl']}"
                f"\nEntry Price: {record['entry']} ORG SL: {record['orgSL']} Trailing SL:{record['trailingSL']} iSL:{record['iSL']}"
                f"\nT1: {record['T1']} T2: {record['T2']} T3:{record['T3']}")

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
        time5 = '5m'
        data5 = self.TradeInd.newSignalData[time5].data
        data5 = data5.reset_index()

        last_result = self.TradeInd.rData.iloc[-1]['result'] if len(self.TradeInd.rData) else ''
        lastIRBLong = data5.iloc[-2]['IRBLONG']
        lastIRBShort = data5.iloc[-2]['IRBSHORT']

        secondLastIRBLong = data5.iloc[-3]['IRBLONG']
        secondLastIRBShort = data5.iloc[-3]['IRBSHORT']

        if lastIRBLong or lastIRBShort:
            self.Trade.entry = data5.iloc[-2]['High']
            self.Trade.orgStopLoss = self.Trade.trailingSL = self.Trade.iSL = data5.iloc[-2]['Low']
            self.Trade.buySell = 'BUY'

        elif secondLastIRBLong or secondLastIRBShort:
            self.Trade.entry = data5.iloc[-3]['High']
            self.Trade.orgStopLoss = self.Trade.trailingSL = self.Trade.iSL = data5.iloc[-3]['Low']
            self.Trade.buySell = 'BUY'

        if lastIRBLong and secondLastIRBLong:
            minHigh = min(data5.iloc[-2]['High'], data5.iloc[-3]['High'])
            minLow = min(data5.iloc[-2]['Low'], data5.iloc[-3]['Low'])

            self.Trade.entry = minHigh
            self.Trade.orgStopLoss = self.Trade.trailingSL = self.Trade.iSL = minLow
            self.Trade.buySell = 'BUY'

    def setSellTrade(self):
        # get last candle for the 5 min with IRB buy or sell
        time5 = '5m'
        data5 = self.TradeInd.newSignalData[time5].data
        data5 = data5.reset_index()

        last_result = self.TradeInd.rData.iloc[-1]['result'] if len(self.TradeInd.rData) else ''
        lastIRBLong = data5.iloc[-2]['IRBLONG']
        lastIRBShort = data5.iloc[-2]['IRBSHORT']

        secondLastIRBLong = data5.iloc[-3]['IRBLONG']
        secondLastIRBShort = data5.iloc[-3]['IRBSHORT']

        if lastIRBLong or lastIRBShort:
            self.Trade.entry = data5.iloc[-2]['Low']
            self.Trade.orgStopLoss = self.Trade.trailingSL = self.Trade.iSL = data5.iloc[-2]['High']
            self.Trade.buySell = 'SELL'

        elif secondLastIRBLong or secondLastIRBShort:
            self.Trade.entry = data5.iloc[-3]['Low']
            self.Trade.orgStopLoss = self.Trade.trailingSL = self.Trade.iSL = data5.iloc[-3]['High']
            self.Trade.buySell = 'SELL'

        if lastIRBShort and secondLastIRBShort:
            maxLow = max(data5.iloc[-2]['Low'], data5.iloc[-3]['Low'])
            maxHigh = max(data5.iloc[-2]['Low'], data5.iloc[-3]['Low'])

            self.Trade.entry = maxLow
            self.Trade.orgStopLoss = self.Trade.trailingSL = self.Trade.iSL = maxHigh
            self.Trade.buySell = 'SELL'

    # this function will decide the target point
    def setTarget(self):
        time5 = '5m'
        data5 = self.TradeInd.newSignalData[time5].data
        data5 = data5.reset_index()

        last_result = self.TradeInd.rData.iloc[-1]['result'] if len(self.TradeInd.rData) else ''

        close = data5.iloc[-2]['Close']

        lastIRB = data5.iloc[-2]['IRBLONG'] or data5.iloc[-2]['IRBSHORT']
        secondLastIRB = data5.iloc[-3]['IRBLONG'] or data5.iloc[-3]['IRBSHORT']

        last_result = last_result.lower()
        if 'buy' in last_result and (lastIRB or secondLastIRB):
            self.setTargetBuy(close=close)

        if 'sell' in last_result and (lastIRB or secondLastIRB):
            self.setTargetSell(close=close)

    def setTargetBuy(self, close):

        if self.TradeInd.r3 < close < self.TradeInd.tHigh:
            self.Trade.Target1 = self.TradeInd.tHigh
            self.Trade.pivotTarget = self.Trade.Target1
            self.Trade.Target2 = self.TradeInd.tHigh
            self.Trade.Target3 = self.TradeInd.tHigh

        if self.TradeInd.r2 < close < self.TradeInd.r3:
            self.Trade.Target1 = self.TradeInd.r3
            self.Trade.pivotTarget = self.Trade.Target1
            self.Trade.Target2 = self.TradeInd.tHigh
            self.Trade.Target3 = self.TradeInd.tHigh

        if self.TradeInd.r1 < close < self.TradeInd.r2:
            self.Trade.Target1 = self.TradeInd.r2
            self.Trade.pivotTarget = self.Trade.Target1
            self.Trade.Target2 = self.TradeInd.r3
            self.Trade.Target3 = self.TradeInd.tHigh

        if self.TradeInd.pivot < close < self.TradeInd.r1:
            self.Trade.Target1 = self.TradeInd.r1
            self.Trade.pivotTarget = self.Trade.Target1
            self.Trade.Target2 = self.TradeInd.r2
            self.Trade.Target3 = self.TradeInd.r3

        if self.TradeInd.s1 < close < self.TradeInd.pivot:
            self.Trade.Target1 = self.TradeInd.pivot
            self.Trade.pivotTarget = self.Trade.Target1
            self.Trade.Target2 = self.TradeInd.r1
            self.Trade.Target3 = self.TradeInd.r2

        if self.TradeInd.s2 < close < self.TradeInd.s1:
            self.Trade.Target1 = self.TradeInd.s1
            self.Trade.pivotTarget = self.Trade.Target1
            self.Trade.Target2 = self.TradeInd.pivot
            self.Trade.Target3 = self.TradeInd.r1

        if self.TradeInd.s3 < close < self.TradeInd.s2:
            self.Trade.Target1 = self.TradeInd.s2
            self.Trade.pivotTarget = self.Trade.Target1
            self.Trade.Target2 = self.TradeInd.s1
            self.Trade.Target3 = self.TradeInd.pivot

        roomLength = self.Trade.entry - self.Trade.orgStopLoss
        self.Trade.rr12 = self.Trade.entry + 2 * roomLength
        self.Trade.rr13 = self.Trade.entry + 3 * roomLength
        self.Trade.rr14 = self.Trade.entry + 4 * roomLength

    def setTargetSell(self, close):

        if self.TradeInd.r2 < close < self.TradeInd.r3:
            self.Trade.Target1 = self.TradeInd.r2
            self.Trade.pivotTarget = self.Trade.Target1
            self.Trade.Target2 = self.TradeInd.r1
            self.Trade.Target3 = self.TradeInd.pivot

        if self.TradeInd.r1 < close < self.TradeInd.r2:
            self.Trade.Target1 = self.TradeInd.r1
            self.Trade.pivotTarget = self.Trade.Target1
            self.Trade.Target2 = self.TradeInd.pivot
            self.Trade.Target3 = self.TradeInd.s1

        if self.TradeInd.pivot < close < self.TradeInd.r1:
            self.Trade.Target1 = self.TradeInd.pivot
            self.Trade.pivotTarget = self.Trade.Target1
            self.Trade.Target2 = self.TradeInd.s1
            self.Trade.Target3 = self.TradeInd.s2

        if self.TradeInd.s1 < close < self.TradeInd.pivot:
            self.Trade.Target1 = self.TradeInd.s1
            self.Trade.pivotTarget = self.Trade.Target1
            self.Trade.Target2 = self.TradeInd.s2
            self.Trade.Target3 = self.TradeInd.s3

        if self.TradeInd.s1 < close < self.TradeInd.s2:
            self.Trade.Target1 = self.TradeInd.s2
            self.Trade.pivotTarget = self.Trade.Target1
            self.Trade.Target2 = self.TradeInd.s3
            self.Trade.Target3 = self.TradeInd.tLow

        if self.TradeInd.s2 < close < self.TradeInd.s3:
            self.Trade.Target1 = self.TradeInd.s3
            self.Trade.pivotTarget = self.Trade.Target1
            self.Trade.Target2 = self.TradeInd.tLow
            self.Trade.Target3 = self.TradeInd.tLow

        if self.TradeInd.s3 < close < self.TradeInd.tLow:
            self.Trade.Target1 = self.TradeInd.tLow
            self.Trade.pivotTarget = self.Trade.Target1
            self.Trade.Target2 = self.TradeInd.tLow
            self.Trade.Target3 = self.TradeInd.tLow

        roomLength = self.Trade.orgStopLoss - self.Trade.entry
        self.Trade.rr12 = self.Trade.entry + 2 * roomLength
        self.Trade.rr13 = self.Trade.entry + 3 * roomLength
        self.Trade.rr14 = self.Trade.entry + 4 * roomLength

    # trail the stoploss to logical point
    def trailStopLoss(self):
        # look for the last 5 min bar hogh/low based on buy sell
        time5 = '5m'
        data5 = self.TradeInd.newSignalData[time5].data
        data5 = data5.reset_index()

        last_result = self.TradeInd.rData.iloc[-1]['result'] if len(self.TradeInd.rData) else ''

        lastIRB = data5.iloc[-2]['IRBLONG'] or data5.iloc[-2]['IRBSHORT']

        last_result = last_result.lower()
        if 'buy' in last_result and lastIRB:
            self.Trade.trailingSL = data5.iloc[-2]['Low']
        else:
            logger.info("Could not trail the SL as the previous candle is not IRB")

        if 'sell' in last_result and lastIRB:
            self.Trade.trailingSL = data5.iloc[-2]['High']
        else:
            logger.info("Could not trail the SL as the previous candle is not IRB")

    def modifyPivotTarget(self):
        if self.Trade.pivotTarget == self.Trade.Target1:
            self.Trade.pivotTarget = self.Trade.Target2
            self.Trade.tradeStatus = f"Target1 hit for {self.Trade.buySell}"

        if self.Trade.pivotTarget == self.Trade.Target2:
            self.Trade.pivotTarget = self.Trade.Target3
            self.Trade.tradeStatus = f"Target2 hit for {self.Trade.buySell}"

        if self.Trade.pivotTarget == self.Trade.Target3:
            self.Trade.pivotTarget = self.Trade.Target3
            self.Trade.tradeStatus = f"Target3 hit for {self.Trade.buySell}"
            self.Trade.tradeOn = False

    def handleTargetHit(self, close):
        self.Trade.exit = close
        self.Trade.tradeOn = True
        self.Trade.endTime = getISTTimeNow()
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
            if (self.Trade.buySell == 'BUY') and (data1.iloc[-2]['Close'] > self.Trade.pivotTarget):
                self.handleTargetHit(data1.iloc[-2]['Close'])
            else:
                self.checkTrailingPossible(data1.iloc[-2]['Close'])

            if (self.Trade.buySell == 'SELL') and (data1.iloc[-2]['Close'] < self.Trade.pivotTarget):
                self.handleTargetHit(data1.iloc[-2]['Close'])
            else:
                self.checkTrailingPossible(data1.iloc[-2]['Close'])

    def checkTrailingPossible(self, min1Close):
        # if moving towards target 50% then move SL to entry if moved close to target 80% then move SL to 50%
        # this will ensure the intermediate profit booking
        # taking reference of rr13 for calculation

        self.trailISL(min1Close)
        if self.Trade.iSLStatus != 'Not set':
            self.trailStopLoss()

    def trailISL(self, min1Close):

        if self.Trade.buySell == 'BUY':
            diff = abs(self.Trade.rr13 - self.Trade.triggerEntryPrice)
            halfWay = self.Trade.triggerEntryPrice + (diff * 0.5)
            eightyPer = self.Trade.triggerEntryPrice + (diff * 0.8)

            if min1Close > halfWay:
                self.Trade.iSL = self.Trade.triggerEntryPrice
                self.Trade.iSLStatus = 'Moved to Entry zero loss'
            if min1Close > eightyPer:
                self.Trade.iSL = halfWay
                self.Trade.iSLStatus = 'Moved to 50% ensure half'
            if min1Close > self.Trade.rr13:
                self.Trade.iSL = self.Trade.rr13
                self.Trade.iSLStatus = 'Moved to R13 ensure 1:3'

        elif self.Trade.buySell == 'SELL':
            diff = abs(self.Trade.rr13 - self.Trade.triggerEntryPrice)
            halfWay = self.Trade.triggerEntryPrice - (diff * 0.5)
            eightyPer = self.Trade.triggerEntryPrice - (diff * 0.8)

            if min1Close > halfWay:
                self.Trade.iSL = self.Trade.triggerEntryPrice
                self.Trade.iSLStatus = 'Moved to Entry zero loss'
            if min1Close > eightyPer:
                self.Trade.iSL = halfWay
                self.Trade.iSLStatus = 'Moved to 50% ensure half'
            if min1Close > self.Trade.rr13:
                self.Trade.iSL = self.Trade.rr13
                self.Trade.iSLStatus = 'Moved to R13 ensure 1:3'

    def isTradeTriggered(self):
        # here we will check if the trade is triggered based on the entry criteria
        # Check that 5 min close is above high for buy and 5 min close below low for sell
        triggered = False
        if self.Trade.entry > 0 and self.Trade.orgStopLoss > 0:
            time5 = '5m'
            data5 = self.TradeInd.newSignalData[time5].data
            data5 = data5.reset_index()
            if self.normalCandle(data5.iloc[-2]['High'], data5.iloc[-2]['Low']):

                if (self.Trade.buySell == 'BUY') and (data5.iloc[-2]['Close'] > self.Trade.entry):
                    triggered = True

            if (self.Trade.buySell == 'SELL') and (data5.iloc[-2]['Close'] < self.Trade.entry):
                    triggered = True

            if triggered:
                self.Trade.tradeOn = True
                self.Trade.triggerEntryPrice = data5.iloc[-2]['Close']
                self.Trade.startTime = getISTTimeNow()
                self.Trade.tradeStatus = 'Triggered'

        return triggered

    def normalCandle(self, high, low):
        stat = False
        triggerCandleSpan = high - low
        length = 50
        entryCandleSpan = abs(self.Trade.entry - self.Trade.orgStopLoss)

        if triggerCandleSpan < 2 * entryCandleSpan and entryCandleSpan < length:
            stat = True
        else:
            logger.info(f"EntryCandleSpan: {entryCandleSpan} Trigger span: {triggerCandleSpan} "
                        f"\nRULE:Trigger candle span < {2 * entryCandleSpan} and Entry candle span < {length} ")
        return stat

    def handleSLHit(self, close, trailing=False, iSL=False):
        self.Trade.exit = close
        self.Trade.endTime = getISTTimeNow()
        self.Trade.tradeOn = False
        self.Trade.pnl = self.Trade.exit - self.Trade.triggerEntryPrice

        if self.Trade.buySell == 'SELL':
            self.Trade.pnl = self.Trade.triggerEntryPrice - self.Trade.exit

        self.Trade.tradeStatus = f"Original SL hit for {self.Trade.buySell}"

        if trailing:
            self.Trade.tradeStatus = f"Trailing SL hit for {self.Trade.buySell}"
            self.Trade.pnl = abs(self.Trade.pnl)
        if iSL:
            self.Trade.tradeStatus = f"Intelligent SL hit for {self.Trade.buySell}"
            self.Trade.pnl = abs(self.Trade.pnl)

        self.Trade.pnl = round(self.Trade.pnl, 2)

        self.recordTrade()

    # this function will decide if the stoploss/trailing stoploss is hit
    def isStopLossHit(self):
        if self.Trade.tradeOn:
            time5 = '5m'
            data5 = self.TradeInd.newSignalData[time5].data
            data5 = data5.reset_index()
            if (self.Trade.buySell == 'BUY') and (data5.iloc[-2]['Close'] < self.Trade.orgStopLoss):
                self.handleSLHit(data5.iloc[-2]['Close'])

            if (self.Trade.buySell == 'SELL') and (data5.iloc[-2]['Close'] > self.Trade.orgStopLoss):
                self.handleSLHit(data5.iloc[-2]['Close'])

            if (self.Trade.buySell == 'BUY') and (data5.iloc[-2]['Close'] < self.Trade.trailingSL):
                if self.Trade.trailingSL != self.Trade.orgStopLoss:
                    self.handleSLHit(data5.iloc[-2]['Close'], trailing=True)

            if (self.Trade.buySell == 'SELL') and (data5.iloc[-2]['Close'] > self.Trade.trailingSL):
                if self.Trade.trailingSL != self.Trade.orgStopLoss:
                    self.handleSLHit(data5.iloc[-2]['Close'], trailing=True)

            if (self.Trade.buySell == 'BUY') and (data5.iloc[-2]['Close'] < self.Trade.iSL):
                if self.Trade.iSL != self.Trade.orgStopLoss:
                    self.handleSLHit(data5.iloc[-2]['Close'], iSL=True)

            if (self.Trade.buySell == 'SELL') and (data5.iloc[-2]['Close'] > self.Trade.iSL):
                if self.Trade.iSL != self.Trade.orgStopLoss:
                    self.handleSLHit(data5.iloc[-2]['Close'], iSL=True)

    def runTrade(self):
        pass

    def forceExit(self):
        pass

    def exit(self):
        pass
