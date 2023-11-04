import threading

stop_event = threading.Event()
restart_event = threading.Event()

from Indicator import Indicator
import time
from Util import getISTTimeNow
from TelgramCom import TemBot

import sys
sys.setrecursionlimit(5000)  # Set the recursion limit to a higher value


def executeRun():
    last_execution_time = None  # Store the last execution time
    ind = Indicator()
    bot = TemBot()
    while not stop_event.is_set():

        try:
            current_time = getISTTimeNow()

            if restart_event.is_set():
                ind = Indicator()
                restart_event.clear()
                print(f"Restarted at {current_time}")
                bot.sendMessage(f"{'Restarted at'} {current_time}")

            if last_execution_time is None or (current_time - last_execution_time).seconds > 60:
                # Perform your tasks here
                print("Executing the task...")

                ind.execute()

                # Update the last execution time
                last_execution_time = getISTTimeNow()
                print('Last Execution time', current_time)

            # Adding a delay to prevent the loop from consuming too much CPU
            # Adjust the sleep time based on your requirements
            time.sleep(60)  # Delay of 60 seconds

        # Catch any other exceptions
        except Exception as e:
            message = f"An error occurred: {e}"
            print(message)
            bot.sendMessage(message)
            last_execution_time = getISTTimeNow()

            restart_event.set()
            time.sleep(300)  # Delay of 300 seconds
            continue

    print("Executing the task END...")


def checkExe():
    global stop_event
    bot = TemBot()
    while True:

        try:
            response = bot.getResponse().lower()

            if response == 'restart' or response == 'r':
                restart_event.set()

            # user_input = input("Press 'x' to stop the loop: ")
            if response == 'x' or response == 'stop':
                stop_event.set()
                break

            time.sleep(30)  # Delay of 30 seconds
        except Exception as e:
            continue



# Create threads
thread1 = threading.Thread(target=checkExe)
thread2 = threading.Thread(target=executeRun)


def start():
    # Start the threads
    thread1.start()
    thread2.start()

    # Wait for the threads to complete (optional)
    thread1.join()
    thread2.join()


#Entry fucntion
start()