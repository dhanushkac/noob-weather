# Python libraries that we need to import for our bot
import random
from flask import Flask, request
from pymessenger.bot import Bot
import requests
import json

app = Flask(__name__)
ACCESS_TOKEN = 'EAARgYhgQdwABANLTtwMYsmqPrV2kGbF88IrPgEm24Jku1qgNjn6gv7rBtE6617pKO3n6OSectEuiJZC79VZBjC2cHATE8vsONpWZCv2RJVbV1BgskZAVzmm4Jma8r37BtRLDGNj907xIWHOmBVZBPzgvdaVLlZADqK5ZBHq7JquhwZDZD'
VERIFY_TOKEN = 'dhanushkabro'
bot = Bot(ACCESS_TOKEN)
BASE_URL = 'http://api.openweathermap.org/data/2.5/weather?appid=7cf5d8961ea0214a980859a54766e28f&units=metric'

quick_replies_list = [{
    "content_type": "location",
},
    {
    "content_type": "text",
    "title": "Other Location",
    "payload": "other",
}
]

# We will receive messages that Facebook sends our bot at this endpoint
@app.route("/", methods=['GET', 'POST'])
def receive_message():
    if request.method == 'GET':
        """Before allowing people to message your bot, Facebook has implemented a verify token
        that confirms all requests that your bot receives came from Facebook."""
        token_sent = request.args.get("hub.verify_token")
        return verify_fb_token(token_sent)
    # if the request was not get, it must be POST and we can just proceed with sending a message back to user
    else:
        # get whatever message a user sent the bot
        output = request.get_json()
        for event in output['entry']:
            messaging = event['messaging']
            for message in messaging:
                if message.get('message'):
                    # Facebook Messenger ID for user so we know where to send response back to
                    recipient_id = message['sender']['id']
                    init_msg = ['hi', 'hey', 'yo', 'bro', 'broo',
                                'machan', 'meh', 'ado', 'adoo', 'oi',  'oii']
                    if message['message'].get('text'):
                        if message['message'].get('text').lower() in init_msg:
                            init(recipient_id)
                        elif message['message'].get('text') == "Other Location":
                            send_message(
                                recipient_id, "Okay.. Send me the city name")
                        else:
                            send_weather_by_city_name(
                                recipient_id, message['message'].get('text'))
                    # if user sends us a GIF, photo,video, or any other non-text item
                    if message['message'].get('attachments'):
                        if message['message'].get('attachments')[0].get("type") == "location":
                            lat = message['message'].get('attachments')[0].get(
                                "payload").get("coordinates").get("lat")
                            lon = message['message'].get('attachments')[0].get(
                                "payload").get("coordinates").get("lon")

                            send_weather_by_lat_lon(recipient_id, lat, lon)
                        else:
                            response_sent_nontext = "Hmmm... not a fan of attachments, prefer locations <3"
                            send_message(recipient_id, response_sent_nontext)
    return "Message Processed"


def verify_fb_token(token_sent):
    # take token sent by facebook and verify it matches the verify token you sent
    # if they match, allow the request, else return an error
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'


def send_weather_by_city_name(recipient_id, location):
    url = BASE_URL + '&q=' + location.lower()
    response = call_weather_api(url)

    send_response(recipient_id, response)


def send_weather_by_lat_lon(recipient_id, lat, lon):
    url = BASE_URL + '&lat=' + str(lat) + '&lon=' + str(lon)
    response = call_weather_api(url)

    send_response(recipient_id, response)


def send_response(recipient_id, response):
    if response.json().get("cod") == 200:
        send_message(recipient_id, get_response_text(response))
    elif response.json().get("cod") == 404:
        send_message(
            recipient_id, 'Hmm... 🤔 No city found, please provide a correct city name')
        init(recipient_id)


def get_response_text(response):
    return_txt = 'It is ' + str(response.json().get("main").get("temp")) + ' at ' + \
        response.json().get("name") + ',' + \
        response.json().get("sys").get("country") + ' now.'

    if response.json().get("weather")[0].get("main").lower().find("rain") != -1:
        return_txt += "\n\nBy the way, better to have a coat. It is raining."
    elif response.json().get("weather")[0].get("main").lower().find("snow") != -1:
        return_txt += "\n\nBy the way, better to have a coat. It is snowing."
    
    return_txt += getIcon(response.json().get("weather")[0].get("icon"))

    return return_txt

def getIcon(icon):
    if icon == "01d" or icon == "02d": #clear
        return '☀⛅'
    elif icon == "01n" or icon == "02n": #clear
        return '🌔☁'
    elif icon == '03d' or icon == '04d': #cloud
        return '☁☁'
    elif icon == '09d' or icon == '10d': #rain
        return '🌦🌧'
    elif icon == '11d' or icon == '11n': #thunder
        return '🌩🌩'
    elif icon == '13d' or icon == '13n':
        return '❄❄❄'
    elif icon == '50d' or icon == '50n':
        return '🌫🌫🌫'


def call_weather_api(url):
    return requests.get(url)


def init(recipient_id):
    requests.post("https://graph.facebook.com/v2.6/me/messages",
                  params={"access_token": ACCESS_TOKEN},
                  data=json.dumps({
                      "recipient": {"id": recipient_id},
                      "message": {"text": "Hey, It's Noob Weather!! Send me a location",
                                  "quick_replies": quick_replies_list}
                  }),
                  headers={'Content-type': 'application/json'})


# uses PyMessenger to send response to user
def send_message(recipient_id, response):
    # sends user the text message provided via input response parameter
    bot.send_text_message(recipient_id, response)
    return "success"


if __name__ == "__main__":
    app.run()
