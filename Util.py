from datetime import datetime
import pytz

import logging


def getISTTimeNow():
    # Set the timezone to Indian Standard Time
    IST = pytz.timezone('Asia/Kolkata')
    # Get the current time in IST
    ist_time = datetime.now(IST)

    date_string = ist_time.strftime("%Y-%m-%d %H:%M:%S")
    # Convert string to datetime object
    datetime_objectNow = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")

    return datetime_objectNow


# Set up the logger
logger = logging.getLogger('BOT')
logger.setLevel(logging.INFO)

# Create a file handler
file_handler = logging.FileHandler('0bot.log')
file_handler.setLevel(logging.DEBUG)

# Create a console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# Set the custom function for formatting the time
# formatter.converter = getISTTimeNow

file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)

'''
# Create a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create a file handler
handler = logging.FileHandler('logfile.log')
handler.setLevel(logging.INFO)

# Get the current time in IST
ist = pytz.timezone('Asia/Kolkata')
ist_time = datetime.now(ist)

# Create a logging format with IST time
formatter = logging.Formatter(f'%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S %Z%z')
handler.setFormatter(formatter)

# This sets the time of the logger to IST
#logging.Formatter.converter = lambda *args: datetime.now(tz=pytz.timezone('Asia/Kolkata'))

# Add the handlers to the logger
logger.addHandler(handler)
'''
