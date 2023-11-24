import schedule
import time
import threading

from ibbbotEntry import executeRun
from ibbbotEntry import continueExecution
import ibbbotEntry as ibb

#import sys

#sys.setrecursionlimit(5000)  # Set the recursion limit to a higher value

# executeRun()
run = [True]


def job():
    global run
    if run[0] is False:
        return False
    if not continueExecution():
        run[0] = False
        return False
    else:
        run[0] = executeRun()
        return True


# Schedule the job to run every 60 seconds
schedule.every(60).seconds.do(job)

# Add any other scheduled jobs here

# Keep the program running to continue the scheduled jobs
while run[0] is True and not ibb.terminate_event.is_set():
    schedule.run_pending()
    time.sleep(60)
