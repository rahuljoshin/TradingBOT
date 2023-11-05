import threading

stop_event = threading.Event()
restart_event = threading.Event()
terminate_event = threading.Event()

from Indicator import Indicator

from TelgramCom import TemBot
from Util import getISTTimeNow

ind = Indicator()


def executeRun():
    checkExe()
    bot = TemBot()
    if terminate_event.is_set():
        bot.sendMessage("TERMINATED")
        return False


    try:
        if restart_event.is_set():
            ind.reset()
            bot.sendMessage("RESTARTED")
            restart_event.clear()
            stop_event.clear()

        if not stop_event.is_set():

            ind.execute()
            current_time = getISTTimeNow()
            msg = f"Execute SUCCESS at {current_time}"
            print(msg)
            bot.sendMessage(msg)
        else:
            bot.sendMessage("STOPPED")



    except Exception as e:
        message = f"An error occurred: {e}"
        print(message)
        bot.sendMessage(message)

    #print("Executing the task END...")
    return True


def checkExe():
    global stop_event, restart_event, terminate_event
    bot = TemBot()

    try:
        response = bot.getResponse().lower()

        if response == 'restart' or response == 'r':
            restart_event.set()


        # user_input = input("Press 'x' to stop the loop: ")
        if response == 'x' or response == 'stop':
            stop_event.set()

        if response == 'terminate':
            terminate_event.set()

    except Exception as e:
        message = f"An error occurred: {e}"
        print(message)
        bot.sendMessage(message)
