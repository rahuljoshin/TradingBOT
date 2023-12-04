from TradeTrigger import Trade
from Derivatives import NSE

from TradeTrigger import TradeTrigger


class OptionTrader:
    name = 'BANKNIFTY'
    expiry = 'weekly or monthly'
    nse = NSE()
    step = 100
    bank_nifty_option_chain = nse.get_option_chain(
        ticker=name,
        is_index=True
    )

    tradeTrigger = TradeTrigger()

    def execute(self, tradeTrigger):
        self.tradeTrigger = tradeTrigger
        self.init()

    def init(self):
        time5 = '5m'
        data5 = self.tradeTrigger.TradeInd.newSignalData[time5].data
        data5 = data5.reset_index()
        close = data5.iloc[-2]['Close']
        atMoney = inMoney = outMoney = (close // 100) * 100
        strikePrice = 'CE_strikePrice'
        identifier = 'CE_identifier'

        if self.tradeTrigger.Trade.buySell == 'BUY':
            inMoney = atMoney - self.step
            outMoney = atMoney + self.step

        if self.tradeTrigger.Trade.buySell == 'SELL':
            inMoney = atMoney + self.step
            outMoney = atMoney - self.step
            strikePrice = 'PE_strikePrice'
            idetifier = 'PE_identifier'

        atmoney = self.bank_nifty_option_chain[self.bank_nifty_option_chain[strikePrice] == atMoney][identifier].values[0]
        inmoney = self.bank_nifty_option_chain[self.bank_nifty_option_chain[strikePrice] == atMoney][identifier].values[0]
        outmoney = self.bank_nifty_option_chain[self.bank_nifty_option_chain[strikePrice] == atMoney][identifier].values[0]


    def decideINATOUT(self):
        pass

    def setInMoney(self):
        pass

    def setOutOfMoney(self):
        pass

    def setAtMoney(self):
        pass



