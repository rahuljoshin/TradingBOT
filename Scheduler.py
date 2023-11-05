import schedule
import time
import threading

from ibbbotEntry import executeRun
import ibbbotEntry as ibb

import sys
sys.setrecursionlimit(5000)  # Set the recursion limit to a higher value

def job():
     executeRun()

# Schedule the job to run every 30 seconds
schedule.every(60).seconds.do(job)

# Add any other scheduled jobs here

# Keep the program running to continue the scheduled jobs
while not ibb.terminate_event.is_set():
    schedule.run_pending()
    time.sleep(60)