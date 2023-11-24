import schedule
import time
import threading

from ibbbotEntry import executeRun
from ibbbotEntry import continueExecution
import ibbbotEntry as ibb

import sys

sys.setrecursionlimit(5000)  # Set the recursion limit to a higher value

# executeRun()
run = [True]


def job():
    if run[0] is False:
        return False
    if run[0] is False or not continueExecution():
        run[0] = False
        return False
    else:
        run[0] = executeRun()


# Schedule the job to run every 30 seconds
schedule.every(60).seconds.do(job)

# Add any other scheduled jobs here

# Keep the program running to continue the scheduled jobs
while not ibb.terminate_event.is_set():
    schedule.run_pending()
    time.sleep(60)
