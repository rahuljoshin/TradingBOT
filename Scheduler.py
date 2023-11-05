import schedule
import time

def job():
    print("Job is running...")

# Schedule the job to run every 5 seconds
schedule.every(5).seconds.do(job)

# Add any other scheduled jobs here

# Keep the program running to continue the scheduled jobs
while True:
    schedule.run_pending()
    time.sleep(1)