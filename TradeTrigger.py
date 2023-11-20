from Indicator import Indicator
from datetime import datetime
from Util import logger

class Trade:
    startTime = datetime(year=1, month=1, day=1, hour=0, minute=0, second=0)
    endTime = datetime(year=1, month=1, day=1, hour=0, minute=0, second=0)
    entry = -1.0
    exit = -1.0
    orgStopLoss = -1.0
    trailingSL = -1.0
    Target1 = -1.0
    Target2 = -1.0
    Target3 = -1.0
    tradeOn = False
    buySell = 'WAIT'
    pnl = 0.0

    def __init__(self):
        self.reset()

    def reset(self):
        self.starttime = datetime(year=1, month=1, day=1, hour=0, minute=0, second=0)
        self.endtime = datetime(year=1, month=1, day=1, hour=0, minute=0, second=0)
        self.entry = -1.0
        self.exit = -1.0
        self.orgStopLoss = -1.0
        self.trailingSL = -1.0
        self.Target1 = -1.0
        self.Target2 = -1.0
        self.Target3 = -1.0
        self.buySell = 'WAIT'
        self.pnl = 0.0


class TradeTrigger:

    Trade = Trade()
    TradeInd = Indicator()

    def __init__(self):

        self.Trade = Trade()

    def reset(self):
        self.Trade = Trade()
    def execute(self, ind):

        if not self.Trade.tradeOn:
            self.TradeInd = ind
            self.setEntryAndSL()
            self.setTarget()
            self.isTradeTriggered()

        else:
            self.monitorTrade()

    def monitorTrade(self):
        if not self.isStopLossHit():
            if self.isTargetHit():
                self.printTrade()

        else:
            self.printTrade()

    def printTrade(self):

        logger.log(f"'\nTrade start:', {self.Trade.starttime}, 'Trade end:', {self.Trade.starttime}")
        logger.log(f"'\nEntry:', {self.Trade.entry}, 'Exit:', {self.Trade.exit}")
        logger.log(f"'\nPNL:', {self.Trade.pnl}, 'Type:', {self.Trade.buySell}")
        logger.log(f"'\nOrgSL:', {self.Trade.orgStopLoss}, 'TrailngSL:', {self.Trade.trailingSL}")
        logger.log(f"'\nTarget1:', {self.Trade.Target1}, 'Target2:', {self.Trade.Target2}, 'Target3:', {self.Trade.Target3} ")


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
            self.Trade.orgStopLoss = data5.iloc[-2]['Low']
            self.Trade.buySell = 'BUY'

        if 'buy' in last_result and secondLastIRB:
            self.Trade.entry = data5.iloc[-3]['High']
            self.Trade.orgStopLoss = data5.iloc[-3]['Low']
            self.Trade.buySell = 'BUY'

        if 'sell' in last_result and lastIRB:
            self.Trade.entry = data5.iloc[-2]['Low']
            self.Trade.orgStopLoss = data5.iloc[-2]['High']
            self.Trade.buySell = 'SELL'


        if 'sell' in last_result and secondLastIRB:
            self.Trade.entry = data5.iloc[-3]['Low']
            self.Trade.orgStopLoss = data5.iloc[-3]['High']
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

        if self.TradeInd.r1 < close < self.TradeInd.r2:
            self.Trade.Target1 = self.TradeInd.r2
            self.Trade.Target2 = self.TradeInd.r3
            self.Trade.Target3 = self.TradeInd.r3

        if self.TradeInd.pivot < close < self.TradeInd.r1:
            self.Trade.Target1 = self.TradeInd.r1
            self.Trade.Target2 = self.TradeInd.r2
            self.Trade.Target3 = self.TradeInd.r3

        if self.TradeInd.s1 < close < self.TradeInd.pivot:
            self.Trade.Target1 = self.TradeInd.pivot
            self.Trade.Target2 = self.TradeInd.r1
            self.Trade.Target3 = self.TradeInd.r2

        if self.TradeInd.s2 < close < self.TradeInd.s1:
            self.Trade.Target1 = self.TradeInd.s1
            self.Trade.Target2 = self.TradeInd.pivot
            self.Trade.Target3 = self.TradeInd.r1

        if self.TradeInd.s3 < close < self.TradeInd.s2:
            self.Trade.Target1 = self.TradeInd.s2
            self.Trade.Target2 = self.TradeInd.s1
            self.Trade.Target3 = self.TradeInd.pivot

    def setTargetSell(self, close):

        if self.TradeInd.r2 < close < self.TradeInd.r3:
            self.Trade.Target1 = self.TradeInd.r2
            self.Trade.Target2 = self.TradeInd.r1
            self.Trade.Target3 = self.TradeInd.pivot

        if self.TradeInd.r1 < close < self.TradeInd.r2:
            self.Trade.Target1 = self.TradeInd.r1
            self.Trade.Target2 = self.TradeInd.pivot
            self.Trade.Target3 = self.TradeInd.s1

        if self.TradeInd.pivot < close < self.TradeInd.r1:
            self.Trade.Target1 = self.TradeInd.pivot
            self.Trade.Target2 = self.TradeInd.s1
            self.Trade.Target3 = self.TradeInd.s2

        if self.TradeInd.s1 < close < self.TradeInd.pivot:
            self.Trade.Target1 = self.TradeInd.s1
            self.Trade.Target2 = self.TradeInd.s2
            self.Trade.Target3 = self.TradeInd.s3

        if self.TradeInd.s1 < close < self.TradeInd.s2:
            self.Trade.Target1 = self.TradeInd.s2
            self.Trade.Target2 = self.TradeInd.s3
            self.Trade.Target3 = self.TradeInd.s3

    # trail the stoploss to logical point
    def trailStopLoss(self):
        self.Trade.trailingSL = (self.Trade.Target1 + self.Trade.Target2) / 2
        self.Trade.Target1 = self.Trade.Target2
        self.Trade.Target2 = self.Trade.Target3

    # this function will decide if the target is hit
    def isTargetHit(self):
        if self.Trade.tradeOn:
            time1 = '1m'
            data1 = self.TradeInd.newSignalData[time1].data
            data1 = data1.reset_index()
            if (self.Trade.buySell == 'BUY') and (data1.iloc[-2]['Close'] > self.Trade.Target1):
                self.Trade.exit = data1.iloc[-2]['Close']
                self.Trade.tradeOn = True
                self.Trade.endtime = datetime.now()
                self.Trade.pnl += self.Trade.exit - self.Trade.entry
                self.trailStopLoss()

            if (self.Trade.buySell == 'SELL') and (data1.iloc[-2]['Close'] < self.Trade.Target1):
                self.Trade.exit = data1.iloc[-2]['Close']
                self.Trade.tradeOn = True
                self.Trade.endtime = datetime.now()
                self.Trade.pnl += self.Trade.entry - self.Trade.exit
                self.trailStopLoss()

    def isTradeTriggered(self):
        #here we will check if the trade is triggered based on the entry criteria
        #Check that 5 min close is above high for buy and 5 min close below low for sell
        if self.Trade.entry > 0 and self.Trade.orgStopLoss > 0:
            time5 = '5m'
            data5 = self.TradeInd.newSignalData[time5].data
            data5 = data5.reset_index()
            if (self.Trade.buySell == 'BUY') and (data5.iloc[-2]['Close'] > self.Trade.entry):
                self.Trade.tradeOn = True
                self.Trade.startTime = datetime.now()

            if (self.Trade.buySell == 'SELL') and (data5.iloc[-2]['Close'] < self.Trade.entry):
                self.Trade.tradeOn = True
                self.Trade.startTime = datetime.now()

        return self.Trade.tradeOn



    # this function will decide if the stoploss/trailing stoploss is hit
    def isStopLossHit(self):
        if self.Trade.tradeOn:
            time5 = '5m'
            data5 = self.TradeInd.newSignalData[time5].data
            data5 = data5.reset_index()
            if (self.Trade.buySell == 'BUY') and (data5.iloc[-2]['Close'] < self.Trade.orgStopLoss):
                self.Trade.exit = data5.iloc[-2]['Close']
                self.Trade.tradeOn = False
                self.Trade.pnl = self.Trade.exit - self.Trade.entry

            if (self.Trade.buySell == 'SELL') and (data5.iloc[-2]['Close'] > self.Trade.orgStopLoss):
                self.Trade.exit = data5.iloc[-2]['Close']
                self.Trade.tradeOn = False
                self.Trade.pnl = self.Trade.entry - self.Trade.exit

            if self.Trade.trailingSL > 0 and self.Trade.tradeOn:

                if (self.Trade.buySell == 'BUY') and (data5.iloc[-2]['Close'] < self.Trade.trailingSL):
                        self.Trade.exit = data5.iloc[-2]['Close']
                        self.Trade.tradeOn = False
                        self.Trade.pnl += self.Trade.exit - self.Trade.entry

                if (self.Trade.buySell == 'SELL') and (data5.iloc[-2]['Close'] > self.Trade.trailingSL):
                        self.Trade.exit = data5.iloc[-2]['Close']
                        self.Trade.tradeOn = False
                        self.Trade.pnl += self.Trade.entry - self.Trade.exit



    def runTrade(self):
        pass

    def forceExit(self):
        pass

    def exit(self):
        pass
