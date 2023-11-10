from Indicator import Indicator
from datetime import datetime


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


class TradeTrigger:
    Indicator = Indicator()
    Trade = Trade()

    def __init__(self):
        self.Indicator = Indicator()
        self.Trade = Trade()

    def execute(self, ind):
        self.Indicator = ind
        self.setEntryAndSL()
        self.setTarget()


    # this function will decide the entry point
    def setEntryAndSL(self):
        # get last candle for the 5 min with IRB buy or sell
        time5 = '5m'
        data5 = Indicator.newSignalData[time5].data
        data5 = data5.reset_index()

        lastIRB = data5.iloc[-2]['IRBLONG'] or data5.iloc[-2]['IRBSHORT']
        secondLastIRB = data5.iloc[-3]['IRBLONG'] or data5.iloc[-3]['IRBSHORT']

        last_result = Indicator.rData.iloc[-1]['result'] if len(Indicator.rData) else ''

        last_result = last_result.lower()
        if 'buy' in last_result and lastIRB:
            self.Trade.entry = data5.iloc[-2]['High']
            self.Trade.orgStopLoss = data5.iLoc[-2]['Low']

        if 'buy' in last_result and secondLastIRB:
            self.Trade.entry = data5.iloc[-3]['High']
            self.Trade.orgStopLoss = data5.iLoc[-3]['Low']

        if 'sell' in last_result and lastIRB:
            self.Trade.entry = data5.iloc[-2]['Low']
            self.Trade.orgStopLoss = data5.iLoc[-2]['High']

        if 'buy' in last_result and secondLastIRB:
            self.Trade.entry = data5.iloc[-3]['Low']
            self.Trade.orgStopLoss = data5.iLoc[-3]['High']

    # this function will decide the target point
    def setTarget(self):
        time5 = '5m'
        data5 = Indicator.newSignalData[time5].data
        data5 = data5.reset_index()

        last_result = Indicator.rData.iloc[-1]['result'] if len(Indicator.rData) else ''

        close = data5[-2]['Close']

        last_result = last_result.lower()
        if 'buy' in last_result:
            self.setTargetBuy(close=close)

        if 'sell' in last_result:
            self.setTargetSell(close=close)

    def setTargetBuy(self, close):

        if Indicator.r1 < close < Indicator.r2:
            self.Trade.Target1 = Indicator.r2
            self.Trade.Target2 = Indicator.r3
            self.Trade.Target3 = Indicator.r3

        if Indicator.pivot < close < Indicator.r1:
            self.Trade.Target1 = Indicator.r1
            self.Trade.Target2 = Indicator.r2
            self.Trade.Target3 = Indicator.r3

        if Indicator.s1 < close < Indicator.pivot:
            self.Trade.Target1 = Indicator.pivot
            self.Trade.Target2 = Indicator.r1
            self.Trade.Target3 = Indicator.r2

        if Indicator.s2 < close < Indicator.s1:
            self.Trade.Target1 = Indicator.s1
            self.Trade.Target2 = Indicator.pivot
            self.Trade.Target3 = Indicator.r1

        if Indicator.s3 < close < Indicator.s2:
            self.Trade.Target1 = Indicator.s2
            self.Trade.Target2 = Indicator.s1
            self.Trade.Target3 = Indicator.pivot

    def setTargetSell(self, close):

        if Indicator.r2 < close < Indicator.r3:
            self.Trade.Target1 = Indicator.r2
            self.Trade.Target2 = Indicator.r1
            self.Trade.Target3 = Indicator.pivot

        if Indicator.r1 < close < Indicator.r2:
            self.Trade.Target1 = Indicator.r1
            self.Trade.Target2 = Indicator.pivot
            self.Trade.Target3 = Indicator.s1

        if Indicator.pivot < close < Indicator.r1:
            self.Trade.Target1 = Indicator.pivot
            self.Trade.Target2 = Indicator.s1
            self.Trade.Target3 = Indicator.s2

        if Indicator.s1 < close < Indicator.pivot:
            self.Trade.Target1 = Indicator.s1
            self.Trade.Target2 = Indicator.s2
            self.Trade.Target3 = Indicator.s3

        if Indicator.s1 < close < Indicator.s2:
            self.Trade.Target1 = Indicator.s2
            self.Trade.Target2 = Indicator.s3
            self.Trade.Target3 = Indicator.s3

    # trail the stoploss to logical point
    def trailStopLoss(self):
        pass

    # this function will decide if the target is hit
    def isTargetHit(self):
        return False

    # this function will decide if the stoploss/trailing stoploss is hit
    def isStopLossHit(self):
        return False

    def runTrade(self):
        pass

    def forceExit(self):
        pass

    def exit(self):
        pass
