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
console_handler.setLevel(logging.DEBUG)

# Create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# Set the custom function for formatting the time
# formatter.converter = getISTTimeNow

file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)

