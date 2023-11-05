
import requests

class TemBot:
    bot_token = '6551575876:AAHFPAxcVaPT0Kqcl0HosnsIqA-j5K2nxng'
    chat_id = '1502486402'  # Replace with your chat ID
    url = f'https://api.telegram.org/bot{bot_token}/'

    def sendMessage(self, message):
        # Telegram bot API URL and your bot token

        url = f"{self.url}{'sendMessage'}"


        #https://api.telegram.org/bot6551575876:AAHFPAxcVaPT0Kqcl0HosnsIqA-j5K2nxng/getUpdates
        # Your chat ID and the message you want to send

        #message = 'This is a test message from your Telegram bot.'

        # Send the message to the bot
        response = requests.post(url, data={'chat_id': self.chat_id, 'text': message})

        #message = '<b>This is a bold message in </b><i><a href="https://www.w3schools.com/colors/colors_picker.asp" style="color:red">red</a></i><b> color.</b>'

        # Send the message to the bot using HTML for formatting
        #response = requests.post(url, data={'chat_id': self.chat_id, 'text': message, 'parse_mode': 'HTML'})

        # Check the response status
        if response.status_code == 200:
            print("Message sent successfully.")
        else:
            print(f"Failed to send the message. Error code: {response.status_code}")
            print(f"Response content: {response.content}")




    def getResponse(self):
        url = f"{self.url}{'getUpdates'}"

        resultMessage = ''

        # Send a GET request to receive updates
        response = requests.get(url)

        # Check if the response is successful
        if response.status_code == 200:
            data = response.json()
            r_chat_id = data['result'][-1]['message']['chat']['id']
            # Get the last message
            if str(r_chat_id) == self.chat_id:
                resultMessage = data['result'][-1]['message']['text']

                print(f"The last message from the bot is: {resultMessage}")
        else:
            print(f"Failed to get updates. Error code: {response.status_code}")

        return resultMessage

        '''
        # Check if the response is successful
        if response.status_code == 200:
            data = response.json()
            # Parse and handle the received updates
            for update in data['result']:
                message = update['message']['text']
                chat_id = update['message']['chat']['id']
                # Handle the message as needed
                if chat_id == self.chat_id:
                    resultMessage = message
                print(f"Received message: {message} from chat ID: {chat_id}")
        else:
            print(f"Failed to get updates. Error code: {response.status_code}")

            '''

