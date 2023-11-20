from Indicator import Indicator
from datetime import datetime
from Util import logger
import pandas as pd


class Trade:
    startTime = datetime(year=1, month=1, day=1, hour=0, minute=0, second=0)
    endTime = datetime(year=1, month=1, day=1, hour=0, minute=0, second=0)
    entry = -1.0
    exit = -1.0
    pnl = 0.0

    orgStopLoss = -1.0
    trailingSL = -1.0
    dynamicTarget = -1.0
    Target1 = -1.0
    Target2 = -1.0
    Target3 = -1.0
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

        self.orgStopLoss = -1.0
        self.trailingSL = -1.0
        self.dynamicTarget = -1.0
        self.Target1 = -1.0
        self.Target2 = -1.0
        self.Target3 = -1.0
        self.buySell = 'WAIT'
        self.tradeStatus = 'Not Triggered'


class TradeTrigger:
    Trade = Trade()
    TradeInd = Indicator()
    columns = ['start', 'end', 'entry', 'exit', 'pnl', 'status', 'ON']

    tradeBook = pd.DataFrame(columns=columns)

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

        else:
            self.monitorTrade()

    def monitorTrade(self):
        self.isStopLossHit()
        self.isTargetHit()
        self.printTrade()
        #self.recordTrade()

    def printTrade(self):

        if self.Trade.tradeOn:
            logger.info(f"\nTrade ON")
        else:
            logger.info(f"\nTrade OFF")

        logger.info(f"'\n'Trade start:' {self.Trade.startTime} 'Trade end:' {self.Trade.endTime} ")
        logger.info(f"'\n'Type:' {self.Trade.buySell} 'Trade status:' {self.Trade.tradeStatus}")
        logger.info(f"'\nEntry:' {self.Trade.entry} 'Exit:' {self.Trade.exit}")
        logger.info(f"'\nPNL:' {self.Trade.pnl} 'Dynamic Target:' {self.Trade.dynamicTarget}")
        logger.info(f"'\nOrgSL:' {self.Trade.orgStopLoss}, 'Trailing-SL:' {self.Trade.trailingSL}")
        logger.info(
            f"'\nTarget1:' {self.Trade.Target1} 'Target2:' {self.Trade.Target2} 'Target3:' {self.Trade.Target3}")

    # this function will decide the entry point
    def setEntryAndSL(self):
        # get last candle for the 5 min with IRB buy or sell
        time5 = '5m'
        data5 = self.TradeInd.newSignalData[time5].data
        data5 = data5.reset_index()

        lastIRB = data5.iloc[-2]['IRBLONG'] or data5.iloc[-2]['IRBSHORT']
        secondLastIRB = data5.iloc[-3]['IRBLONG'] or data5.iloc[-3]['IRBSHORT']

        last_result = self.TradeInd.rData.iloc[-1]['result'] if len(self.TradeInd.rData) else ''

        last_result = last_result.lower()
        if 'buy' in last_result and lastIRB:
            self.Trade.entry = data5.iloc[-2]['High']
            self.Trade.orgStopLoss = self.Trade.trailingSL = data5.iloc[-2]['Low']
            self.Trade.buySell = 'BUY'

        if 'buy' in last_result and secondLastIRB:
            self.Trade.entry = data5.iloc[-3]['High']
            self.Trade.orgStopLoss = self.Trade.trailingSL = data5.iloc[-3]['Low']
            self.Trade.buySell = 'BUY'

        if 'sell' in last_result and lastIRB:
            self.Trade.entry = data5.iloc[-2]['Low']
            self.Trade.orgStopLoss = self.Trade.trailingSL = data5.iloc[-2]['High']
            self.Trade.buySell = 'SELL'

        if 'sell' in last_result and secondLastIRB:
            self.Trade.entry = data5.iloc[-3]['Low']
            self.Trade.orgStopLoss = self.Trade.trailingSL = data5.iloc[-3]['High']
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
        if 'buy' in last_result and lastIRB:
            self.setTargetBuy(close=close)

        if 'buy' in last_result and secondLastIRB:
            self.setTargetBuy(close=close)

        if 'sell' in last_result and lastIRB:
            self.setTargetSell(close=close)

        if 'sell' in last_result and secondLastIRB:
            self.setTargetSell(close=close)

    def setTargetBuy(self, close):

        if self.TradeInd.r3 < close < self.TradeInd.tHigh:
            self.Trade.Target1 = self.TradeInd.tHigh
            self.Trade.dynamicTarget = self.Trade.Target1
            self.Trade.Target2 = self.TradeInd.tHigh
            self.Trade.Target3 = self.TradeInd.tHigh

        if self.TradeInd.r2 < close < self.TradeInd.r3:
            self.Trade.Target1 = self.TradeInd.r3
            self.Trade.dynamicTarget = self.Trade.Target1
            self.Trade.Target2 = self.TradeInd.tHigh
            self.Trade.Target3 = self.TradeInd.tHigh

        if self.TradeInd.r1 < close < self.TradeInd.r2:
            self.Trade.Target1 = self.TradeInd.r2
            self.Trade.dynamicTarget = self.Trade.Target1
            self.Trade.Target2 = self.TradeInd.r3
            self.Trade.Target3 = self.TradeInd.tHigh

        if self.TradeInd.pivot < close < self.TradeInd.r1:
            self.Trade.Target1 = self.TradeInd.r1
            self.Trade.dynamicTarget = self.Trade.Target1
            self.Trade.Target2 = self.TradeInd.r2
            self.Trade.Target3 = self.TradeInd.r3

        if self.TradeInd.s1 < close < self.TradeInd.pivot:
            self.Trade.Target1 = self.TradeInd.pivot
            self.Trade.dynamicTarget = self.Trade.Target1
            self.Trade.Target2 = self.TradeInd.r1
            self.Trade.Target3 = self.TradeInd.r2

        if self.TradeInd.s2 < close < self.TradeInd.s1:
            self.Trade.Target1 = self.TradeInd.s1
            self.Trade.dynamicTarget = self.Trade.Target1
            self.Trade.Target2 = self.TradeInd.pivot
            self.Trade.Target3 = self.TradeInd.r1

        if self.TradeInd.s3 < close < self.TradeInd.s2:
            self.Trade.Target1 = self.TradeInd.s2
            self.Trade.dynamicTarget = self.Trade.Target1
            self.Trade.Target2 = self.TradeInd.s1
            self.Trade.Target3 = self.TradeInd.pivot

    def setTargetSell(self, close):

        if self.TradeInd.r2 < close < self.TradeInd.r3:
            self.Trade.Target1 = self.TradeInd.r2
            self.Trade.dynamicTarget = self.Trade.Target1
            self.Trade.Target2 = self.TradeInd.r1
            self.Trade.Target3 = self.TradeInd.pivot

        if self.TradeInd.r1 < close < self.TradeInd.r2:
            self.Trade.Target1 = self.TradeInd.r1
            self.Trade.dynamicTarget = self.Trade.Target1
            self.Trade.Target2 = self.TradeInd.pivot
            self.Trade.Target3 = self.TradeInd.s1

        if self.TradeInd.pivot < close < self.TradeInd.r1:
            self.Trade.Target1 = self.TradeInd.pivot
            self.Trade.dynamicTarget = self.Trade.Target1
            self.Trade.Target2 = self.TradeInd.s1
            self.Trade.Target3 = self.TradeInd.s2

        if self.TradeInd.s1 < close < self.TradeInd.pivot:
            self.Trade.Target1 = self.TradeInd.s1
            self.Trade.dynamicTarget = self.Trade.Target1
            self.Trade.Target2 = self.TradeInd.s2
            self.Trade.Target3 = self.TradeInd.s3

        if self.TradeInd.s1 < close < self.TradeInd.s2:
            self.Trade.Target1 = self.TradeInd.s2
            self.Trade.dynamicTarget = self.Trade.Target1
            self.Trade.Target2 = self.TradeInd.s3
            self.Trade.Target3 = self.TradeInd.tLow

        if self.TradeInd.s2 < close < self.TradeInd.s3:
            self.Trade.Target1 = self.TradeInd.s3
            self.Trade.dynamicTarget = self.Trade.Target1
            self.Trade.Target2 = self.TradeInd.tLow
            self.Trade.Target3 = self.TradeInd.tLow

        if self.TradeInd.s3 < close < self.TradeInd.tLow:
            self.Trade.Target1 = self.TradeInd.tLow
            self.Trade.dynamicTarget = self.Trade.Target1
            self.Trade.Target2 = self.TradeInd.tLow
            self.Trade.Target3 = self.TradeInd.tLow

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

        if 'sell' in last_result and lastIRB:
            self.Trade.trailingSL = data5.iloc[-2]['High']

    def modifyDynamicTarget(self):
        if self.Trade.dynamicTarget == self.Trade.Target1:
            self.Trade.dynamicTarget = self.Trade.Target2
            self.Trade.tradeStatus = f"Target1 hit for {self.Trade.buySell}"

        if self.Trade.dynamicTarget == self.Trade.Target2:
            self.Trade.dynamicTarget = self.Trade.Target3
            self.Trade.tradeStatus = f"Target2 hit for {self.Trade.buySell}"

        if self.Trade.dynamicTarget == self.Trade.Target3:
            self.Trade.dynamicTarget = self.Trade.Target3
            self.Trade.tradeStatus = f"Target3 hit for {self.Trade.buySell}"
            self.Trade.tradeOn = False

    def recordTrade(self):
        new_row1 = {'start': self.Trade.startTime, 'end': self.Trade.endTime, 'entry': self.Trade.entry,
                    'exit': self.Trade.exit, 'pnl': self.Trade.pnl, 'status': self.Trade.tradeStatus, 'ON': self.Trade.tradeOn}
        self.tradeBook.loc[len(self.tradeBook)] = new_row1


        logger.info("TradeBook Start")
        for index, record in self.tradeBook.iterrows():

            logger.info(
                f"Trade#: {index} ON: {record['ON']} Status: {record['status']} Start Time: {record['start']} Entry Price: {record['entry']} "
                f"Exit Price: {record['exit']} PNL: {record['pnl']} End Time:{record['end']}")

        logger.info("TradeBook End")

        self.tradeBook.to_csv('tradebook.csv', header=True, index=True)

    def handleTargetHit(self, close):
        self.Trade.exit = close
        self.Trade.tradeOn = True
        self.Trade.endTime = datetime.now()
        self.Trade.pnl += abs(self.Trade.exit - self.Trade.entry)

        self.recordTrade()

        self.trailStopLoss()
        self.modifyDynamicTarget()

        # this function will decide if the target is hit

    def isTargetHit(self):
        if self.Trade.tradeOn:
            time1 = '1m'
            data1 = self.TradeInd.newSignalData[time1].data
            data1 = data1.reset_index()
            if (self.Trade.buySell == 'BUY') and (data1.iloc[-2]['Close'] > self.Trade.dynamicTarget):
                self.handleTargetHit(data1.iloc[-2]['Close'])

            if (self.Trade.buySell == 'SELL') and (data1.iloc[-2]['Close'] < self.Trade.dynamicTarget):
                self.handleTargetHit(data1.iloc[-2]['Close'])

    def isTradeTriggered(self):
        # here we will check if the trade is triggered based on the entry criteria
        # Check that 5 min close is above high for buy and 5 min close below low for sell
        triggered = False
        if self.Trade.entry > 0 and self.Trade.orgStopLoss > 0:
            time5 = '5m'
            data5 = self.TradeInd.newSignalData[time5].data
            data5 = data5.reset_index()

            if (self.Trade.buySell == 'BUY') and (data5.iloc[-2]['Close'] > self.Trade.entry):
                triggered = True

            if (self.Trade.buySell == 'SELL') and (data5.iloc[-2]['Close'] < self.Trade.entry):
                triggered = True

            if triggered:
                self.Trade.tradeOn = True
                self.Trade.startTime = datetime.now()
                self.Trade.tradeStatus = 'Triggered'

        return triggered

    def handleSLHit(self, close, trailing=False):
        self.Trade.exit = close
        self.Trade.tradeOn = False
        self.Trade.pnl = self.Trade.exit - self.Trade.entry
        self.Trade.tradeStatus = f"Original SL hit for {self.Trade.buySell}"
        if trailing:
            self.Trade.tradeStatus = f"Trailing SL hit for {self.Trade.buySell}"

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
                self.handleSLHit(data5.iloc[-2]['Close'], trailing=True)

            if (self.Trade.buySell == 'SELL') and (data5.iloc[-2]['Close'] > self.Trade.trailingSL):
                self.handleSLHit(data5.iloc[-2]['Close'], trailing=True)

    def runTrade(self):
        pass

    def forceExit(self):
        pass

    def exit(self):
        pass
