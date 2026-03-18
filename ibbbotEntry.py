import threading
import traceback

stop_event = threading.Event()
restart_event = threading.Event()
terminate_event = threading.Event()

from TradeTrigger import TradeTrigger
from Indicator import Indicator

#from OptionTrader import OptionTrader

from TelgramCom import TemBot
from Util import getISTTimeNow
from Util import logger

ind = Indicator()
tradeTrigger = TradeTrigger()

#optionTrader = OptionTrader()


def continueExecution():
    checkExe()

    if terminate_event.is_set():
        bot = TemBot()
        bot.sendMessage("Final TERMINATED")
        return False

    return True


def executeRun():
    bot = TemBot()
    if terminate_event.is_set():
        bot.sendMessage("Excute TERMINATED")
        return False

    try:
        if restart_event.is_set():
            ind.reset()
            tradeTrigger.reset()

            logger.info("RESTARTED")
            bot.sendMessage("RESTARTED")
            restart_event.clear()
            stop_event.clear()

        if not stop_event.is_set():

            ind.execute()
            tradeTrigger.execute(ind)
            #optionTrader.execute(tradeTrigger)
            current_time = getISTTimeNow()
            msg = f"Execute SUCCESS at {current_time}"
            logger.info(msg)
            #bot.sendMessage(msg)
        else:
            logger.info("STOPPED")
            bot.sendMessage("STOPPED")

    except Exception as e:
        message = f"An error occurred: {e}"

        traceback.print_exc()
        logger.error(message)
        bot.sendMessage(message)

    # print("Executing the task END...")
    return True


def checkExe():
    global stop_event, restart_event, terminate_event
    bot = TemBot()

    try:
        response = bot.getResponse().lower()

        if 'restart' in response or response == 'r':
            restart_event.set()

        if '1r' in response:
            ind.forceRecal(time='1m')

        if '5r' in response:
            ind.forceRecal(time='5m')
        if '15r' in response:
            ind.forceRecal(time='15m')

        if '30r' in response:
            ind.forceRecal(time='30m')

        if 'dr' in response:
            ind.forceRecal(time='1d')

        # user_input = input("Press 'x' to stop the loop: ")
        if response == 'x' or 'stop' in response:
            stop_event.set()

        if 'terminate' in response:
            terminate_event.set()

    except Exception as e:
        message = f"An error occurred: {e}"
        logger.error(message)
        bot.sendMessage(message)
