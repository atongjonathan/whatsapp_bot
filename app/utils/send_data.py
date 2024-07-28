import logging
from flask import jsonify
import os
import requests
import json
import telebot


ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN) 
VERSION = os.environ.get("VERSION")
headers = {
    "Content-type": "application/json",
    "Authorization": f"Bearer {ACCESS_TOKEN}",
}
url = f"https://graph.facebook.com/{VERSION}/{PHONE_NUMBER_ID}/messages"
message_body = json.dumps(
    {
        "messaging_product": "whatsapp",
        "context": ""
    })


def mark_as_read(message_id):
    body = json.dumps(
        {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id
        })
    try:
        response = requests.post(
            url, data=body, headers=headers, timeout=10
        )  # 10 seconds timeout as an example
        # Raises an HTTPError if the HTTP request returned an unsuccessful status code
        response.raise_for_status()
        return jsonify({"status": "Marked", "message": f"message:{message_id} marked as read"}), 200
    except requests.Timeout as e:
        logging.error(e)
        return jsonify({"status": "error", "message": "Failed to mark message as read"}), 500

# def reply_message(message):
#     message_id = message.get("id")
#     if message_type == "text":
#         message_body = message["text"]["body"]
#         send_message(message_body, number, message_type)
#     else:
#         logging.info(message)


def call_api(message_body):
    message_body = json.dumps(message_body)
    try:
        response = requests.post(
            url, data=message_body, headers=headers, timeout=10
        )  # 10 seconds timeout as an example
        # Raises an HTTPError if the HTTP request returned an unsuccessful status code
        response.raise_for_status()
        return jsonify({"status": "Sent successfully"}), 200
    except requests.Timeout:
        logging.error("Timeout occurred while sending message")
        return jsonify({"status": "error", "message": "Request timed out"}), 408
    except (
        requests.RequestException
    ) as e:  # This will catch any general request exception
        logging.error(f"Request failed due with message: {response.text}")
        return jsonify({"status": "error", "message": "Failed to send message"}), 500


def send_message(message):
    message_type = message.get("type")
    body = {
        "messaging_product": "whatsapp",
        "context": {
            "message_id": message.get("id")
        },
        "to": message.get("from"),
        "type": message_type
    }
    if message_type == "text":
        text = message["text"]["body"]
        if "-" in text:
            performer = text.split("-")[0].strip()
            title = text.split("-")[1].strip()
            try:
                url = f"https://api.atongjonathan2.workers.dev/?title={title}&performer={performer}"
                response = requests.get(url)
                response.raise_for_status()
                data = response.json()
                file_id = data["response"]["document"]["file_id"]
                file_info = bot.get_file(file_id) 
                url = 'https://api.telegram.org/file/bot{0}/{1}'.format(TELEGRAM_BOT_TOKEN, file_info.file_path) 
                body["document"] = {
                    "link": url,
                    "caption": f"{performer} = {title}",
                    "filename":f"{performer} = {title}.mp3"
                }              
            except Exception as e:

                body[message_type] = {"preview_url": False, "body": str(e)}
    elif message_type == "contacts":
        #         contact_body = {
        #   "messaging_product": "whatsapp",
        #   "to": "254708683896",
        #   "type": "contacts",
        #   "contacts": [
        #     {
        #       "name": {
        #         "formatted_name": "Jona",
        #         "first_name": "Jonathan",
        #         "last_name": "Atong"
        #       },
        #       "phones": [
        #         {
        #           "phone": "+254708683896",
        #           "type": "CELL"
        #         }
        #       ],
        #       "emails": [
        #         {
        #           "email": "atongjonathan@gmail.com",
        #           "type": "HOME"
        #         }
        #       ],
        #       "addresses": [
        #         {
        #           "street": "Komarock",
        #           "city": "Nairobi",
        #           "state": "NRB",
        #           "zip": "00100",
        #           "country_code": "254",
        #           "country": "KE",
        #           "type": "HOME"
        #         }
        #       ],
        #       "birthday": "2001-11-16",
        #       "org": {
        #         "company": "Peri Bloom",
        #         "department": "Developers",
        #         "title": "Developer"
        #       },
        #       "urls": [
        #         {
        #           "url": "https://peri-bloom.com",
        #           "type": "WORK"
        #         }
        #       ]
        #     }
        #   ]
        # }
        body[message_type] = message["contacts"]
    elif message_type == "image":
        body[message_type] = {
            "id": message["image"]["id"]
        }
        caption = message["image"].get("caption")
        if caption:
            body[message_type]["caption"] = caption
    elif message_type == "video":
        body[message_type] = {
            "id": message["video"]["id"]
        }
        caption = message["video"].get("caption")
        if caption:
            body[message_type]["caption"] = caption
    elif message_type == "audio":
        body[message_type] = {
            "id": message["audio"]["id"]
        }
    elif message_type == "document":
        body[message_type] = {
            "id": message["document"]["id"]
        }
        caption = message["document"].get("caption")
        if caption:
            body[message_type]["caption"] = caption
    else:
        body["text"] = {
            "body": f"This is a {message_type}"
        }

    # logging.info(body[message_type])
    call_api(body)
