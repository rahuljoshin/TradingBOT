

from datetime import datetime
import pytz


def getISTTimeNow():
    # Get the current time in the UTC timezone
    utc_now = datetime.now(pytz.utc)

    # Convert the current time to the Indian Standard Time (IST) timezone
    ist_now = utc_now.astimezone(pytz.timezone('Asia/Kolkata'))

    return ist_now
