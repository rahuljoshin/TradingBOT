import pandas as pd
from Derivatives import NSE
from Util import logger
from TradeTrigger import TradeTrigger


from IndHelper import *


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
    atOption = inOption = outOption = pd.DataFrame()


    def execute(self, tradeTrigger):
        self.tradeTrigger = tradeTrigger
        self.init()
        self.confirmBuyOrSell()


    def init(self):
        self.atOption = self.inOption = self.outOption = pd.DataFrame()
        time5 = '5m'
        data5 = self.tradeTrigger.TradeInd.newSignalData[time5].data
        # data5 = data5.reset_index()
        close = data5.iloc[-2]['Close']
        atMoney = inMoney = outMoney = (close // 100) * 100
        strikePrice = 'CE_strikePrice'
        identifier = 'CE_identifier'

        # if self.tradeTrigger.Trade.buySell == 'BUY':
        inMoney = atMoney - self.step
        outMoney = atMoney + self.step

        if self.tradeTrigger.Trade.buySell == 'SELL':
            inMoney = atMoney + self.step
            outMoney = atMoney - self.step
            strikePrice = 'PE_strikePrice'
            identifier = 'PE_identifier'

        atmoneyStr = self.bank_nifty_option_chain[self.bank_nifty_option_chain[strikePrice] ==
                                               atMoney][identifier].values[0]
        inmoneyStr = self.bank_nifty_option_chain[self.bank_nifty_option_chain[strikePrice] ==
                                               inMoney][identifier].values[0]
        outmoneyStr = self.bank_nifty_option_chain[self.bank_nifty_option_chain[strikePrice] ==
                                                outMoney][identifier].values[0]

        self.atOption = self.populateData(atmoneyStr)
        self.inOption = self.populateData(inmoneyStr)
        self.outOption = self.populateData(outmoneyStr)

    def populateData(self, price):

        optionData = self.nse.get_ohlc_data(price, timeframe='5Min', is_index=True)

        # PSAR, RSI9,3,21 and stocastics
        optionData['SAR'] = lib.wrapper.PSARIndicator(high=optionData['high'],
                                                         low=optionData['low'], close=optionData['close']).psar()
        optionData['RSI9'] = lib.wrapper.RSIIndicator(close=optionData['close'], window=9).rsi()
        optionData['EMA3_RSI'] = lib.wrapper.EMAIndicator(optionData['RSI9'], window=3).ema_indicator()

        stoch = lib.wrapper.StochasticOscillator(high=optionData['high'],
                                                  low=optionData['low'], close=optionData['close'],
                                                  window=4,
                                                  smooth_window=1)
        optionData['%K'] = stoch.stoch()
        optionData['%D'] = stoch.stoch_signal()

        # SMA5,20,50 and EMA 18,50
        optionData['SMA5'] = optionData['close'].rolling(window=5).mean()
        optionData['EMA18'] = optionData['close'].ewm(span=18).mean()
        optionData['SMA20'] = optionData['close'].rolling(window=20).mean()
        optionData['SMA50'] = optionData['close'].rolling(window=50).mean()
        optionData['EMA50'] = optionData['close'].ewm(span=50).mean()

        optionData['SMA50'].fillna(optionData['EMA50'], inplace=True)

        # Bollinger band 20,2
        optionData['BBUpperBand'], optionData['BBLowerBand'] = IndHelper.calBB(optionData['close'], period=20,
                                                                                     stddev=2)

        optionData['kUpperBand'], optionData['kMiddleLine'], optionData['kLowerBand'] = (
            IndHelper.calculateKeltnerChannel(optionData['high'],
                                              optionData['low'], optionData['close'], period=20, multiplier=2))

        optionData['TTMSQ'] = (optionData['BBUpperBand'] < optionData['kUpperBand']) & (
                optionData['BBLowerBand'] > optionData['kLowerBand'])

        optionData['diff'] = optionData['close'] - ((optionData['kMiddleLine'] + optionData['SMA20']) / 2)

        optionData['tenkan'], optionData['kijun'], optionData['senkouA'], optionData['senkouB'] = (
            IndHelper.calcSuperIchi(optionData['close'], optionData['high'], optionData['low']))

        optionData['IRBLONG'], optionData['IRBSHORT'] = (
            IndHelper.findIRB(optionData['open'], optionData['high'],
                              optionData['low'], optionData['close']))

        '''
        optionData['Price'] = (optionData['high'] + optionData['low']) / 2
        #optionData['Price_times_Volume'] = optionData['Price'] * optionData['Volume']

        criteria = optionData.index.strftime('%Y-%m-%d')

        optionData['Cumulative_Price_Volume'] = optionData.groupby(criteria)[['Price_times_Volume']].cumsum()

        optionData['Cumulative_Volume'] = optionData.groupby(criteria)[['Volume']].cumsum()

        optionData['VWAP'] = optionData['Cumulative_Price_Volume'] / optionData['Cumulative_Volume']
        '''

        return optionData

    def confirmBuyOrSell(self):
        #check the current ststus of the option value
        #atOption.iloc[-2]['Close'] > data30.iloc[-2]['EMA18']))
        #close5Min = self.atOption['Close']
        pass

    def decideINATOUT(self):
        pass

    def setInMoney(self):
        pass

    def setOutOfMoney(self):
        pass

    def setAtMoney(self):
        pass
