import logging
from flask import jsonify
import os
import requests
import json

ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")
VERSION = os.environ.get("VERSION")
print(ACCESS_TOKEN)
headers = {
    "Content-type": "application/json",
    "Authorization": f"Bearer {ACCESS_TOKEN}",
}
url = f"https://graph.facebook.com/{VERSION}/{PHONE_NUMBER_ID}/messages"
message_body = json.dumps(
    {
        "messaging_product": "whatsapp",
        "context":""
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
        response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
        return jsonify({"status": "Marked", "message": "message:{message_id} marked as read"}), 200
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
        response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
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
          "type":message_type
        }
    if message_type == "text":
        body[message_type] = {"preview_url": False, "body": message["text"]["body"]}
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
        body["text"]  = {
            "body":f"This is a {message_type}"
            }


    logging.info(body[message_type])
    call_api(body)
