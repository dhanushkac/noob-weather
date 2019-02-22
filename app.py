#Python libraries that we need to import for our bot
import random
from flask import Flask, request
from pymessenger.bot import Bot
import requests
import json

app = Flask(__name__)
ACCESS_TOKEN = 'EAARgYhgQdwABANLTtwMYsmqPrV2kGbF88IrPgEm24Jku1qgNjn6gv7rBtE6617pKO3n6OSectEuiJZC79VZBjC2cHATE8vsONpWZCv2RJVbV1BgskZAVzmm4Jma8r37BtRLDGNj907xIWHOmBVZBPzgvdaVLlZADqK5ZBHq7JquhwZDZD'
VERIFY_TOKEN = 'dhanushkabro'
bot = Bot(ACCESS_TOKEN)

#We will receive messages that Facebook sends our bot at this endpoint 
@app.route("/", methods=['GET', 'POST'])
def receive_message():
    if request.method == 'GET':
        """Before allowing people to message your bot, Facebook has implemented a verify token
        that confirms all requests that your bot receives came from Facebook.""" 
        token_sent = request.args.get("hub.verify_token")
        return verify_fb_token(token_sent)
    #if the request was not get, it must be POST and we can just proceed with sending a message back to user
    else:
        # get whatever message a user sent the bot
       output = request.get_json()
       for event in output['entry']:
          messaging = event['messaging']
          for message in messaging:
            if message.get('message'):
                #Facebook Messenger ID for user so we know where to send response back to
                recipient_id = message['sender']['id']
                if message['message'].get('text'):
                    response_sent_text = get_weather(message['message'].get('text'))
                    send_message(recipient_id, response_sent_text)
                #if user sends us a GIF, photo,video, or any other non-text item
                if message['message'].get('attachments'):
                    response_sent_nontext = "Hmmm... not a fan of attachments, prefer locations <3"
                    send_message(recipient_id, response_sent_nontext)
    return "Message Processed"


def verify_fb_token(token_sent):
    #take token sent by facebook and verify it matches the verify token you sent
    #if they match, allow the request, else return an error 
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'


#chooses a random message to send to the user
def get_weather(location):
    base_url = 'http://api.openweathermap.org/data/2.5/weather?appid=7cf5d8961ea0214a980859a54766e28f&units=metric&q='
    response = requests.get(base_url + location.lower())
	
    if "coat" in location.lower() and response.json().get("cod") == 200:
        if "rain" in response.json().get("weather")[0].get("main").toLower():
            return "Yeah.. better to have one. It is rainy here"
        elif "snow" in response.json().get("weather")[0].get("main").toLower():
            return "Yeah.. better to have one. It is snowing at " + location + " now."
    elif response.json().get("cod") == 200:
        return_txt = 'It is ' + str(response.json().get("main").get("temp")) + ' at ' + location + ','
        return_txt += response.json().get("sys").get("country") + 'now. \n'
        return return_txt
    else:
	    return 'Wrong city found, please provide correct city name'

#uses PyMessenger to send response to user
def send_message(recipient_id, response):
    #sends user the text message provided via input response parameter
    bot.send_text_message(recipient_id, response)
    return "success"

if __name__ == "__main__":
    app.run()