

from datetime import datetime
import pytz


def getISTTimeNow():
    # Set the timezone to Indian Standard Time
    ist = pytz.timezone('Asia/Kolkata')

    # Get the current time in IST
    ist_time = datetime.now(ist)

    date_string = ist_time.strftime("%Y-%m-%d %H:%M:%S")
    # Convert string to datetime object
    datetime_objectNow = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")

    return datetime_objectNow
