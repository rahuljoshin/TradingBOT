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

    def execute(self, tradeTrigger):
        self.tradeTrigger = tradeTrigger
        self.init()

    def init(self):
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

        atmoney = self.bank_nifty_option_chain[self.bank_nifty_option_chain[strikePrice] ==
                                               atMoney][identifier].values[0]
        inmoney = self.bank_nifty_option_chain[self.bank_nifty_option_chain[strikePrice] ==
                                               inMoney][identifier].values[0]
        outmoney = self.bank_nifty_option_chain[self.bank_nifty_option_chain[strikePrice] ==
                                                outMoney][identifier].values[0]

        logger.info(f"At money:{atmoney} In Money:{inmoney}, OutMoney:{outmoney}")

        optionDataATM = self.nse.get_ohlc_data(atmoney, timeframe='5Min', is_index=True)
        #optionDataITM = self.nse.get_ohlc_data(inmoney, timeframe='5Min', is_index=True)
        #optionDataOTM = self.nse.get_ohlc_data(outmoney, timeframe='5Min', is_index=True)

        # PSAR, RSI9,3,21 and stocastics
        optionDataATM['SAR'] = lib.wrapper.PSARIndicator(high=optionDataATM['high'],
                                                         low=optionDataATM['low'], close=optionDataATM['close']).psar()
        optionDataATM['RSI9'] = lib.wrapper.RSIIndicator(close=optionDataATM['close'], window=9).rsi()
        optionDataATM['EMA3_RSI'] = lib.wrapper.EMAIndicator(optionDataATM['RSI9'], window=3).ema_indicator()

        stoch = lib.wrapper.StochasticOscillator(high=optionDataATM['high'],
                                                  low=optionDataATM['low'], close=optionDataATM['close'],
                                                  window=4,
                                                  smooth_window=1)
        optionDataATM['%K'] = stoch.stoch()
        optionDataATM['%D'] = stoch.stoch_signal()

        # SMA5,20,50 and EMA 18,50
        optionDataATM['SMA5'] = optionDataATM['close'].rolling(window=5).mean()
        optionDataATM['EMA18'] = optionDataATM['close'].ewm(span=18).mean()
        optionDataATM['SMA20'] = optionDataATM['close'].rolling(window=20).mean()
        optionDataATM['SMA50'] = optionDataATM['close'].rolling(window=50).mean()
        optionDataATM['EMA50'] = optionDataATM['close'].ewm(span=50).mean()

        optionDataATM['SMA50'].fillna(optionDataATM['EMA50'], inplace=True)

        # Bollinger band 20,2
        optionDataATM['BBUpperBand'], optionDataATM['BBLowerBand'] = IndHelper.calBB(optionDataATM['close'], period=20,
                                                                                     stddev=2)

        optionDataATM['kUpperBand'], optionDataATM['kMiddleLine'], optionDataATM['kLowerBand'] = (
            IndHelper.calculateKeltnerChannel(optionDataATM['high'],
                                              optionDataATM['low'], optionDataATM['close'], period=20, multiplier=2))

        optionDataATM['TTMSQ'] = (optionDataATM['BBUpperBand'] < optionDataATM['kUpperBand']) & (
                optionDataATM['BBLowerBand'] > optionDataATM['kLowerBand'])

        optionDataATM['diff'] = optionDataATM['close'] - ((optionDataATM['kMiddleLine'] + optionDataATM['SMA20']) / 2)

        optionDataATM['tenkan'], optionDataATM['kijun'], optionDataATM['senkouA'], optionDataATM['senkouB'] = (
            IndHelper.calcSuperIchi(optionDataATM['close'], optionDataATM['high'], optionDataATM['low']))

        optionDataATM['IRBLONG'], optionDataATM['IRBSHORT'] = (
            IndHelper.findIRB(optionDataATM['open'], optionDataATM['high'],
                              optionDataATM['low'], optionDataATM['close']))

        print(optionDataATM)

    def decideINATOUT(self):
        pass

    def setInMoney(self):
        pass

    def setOutOfMoney(self):
        pass

    def setAtMoney(self):
        pass
