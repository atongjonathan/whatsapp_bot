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


def send_text(chat_id, text, message_id):
    body = {
        "messaging_product": "whatsapp",
        "context": {
            "message_id": message_id
        },
        "to": chat_id ,
        "type": "text",
        "text": {
            "preview_url": True,
            "body": text
        }
    }
    call_api(body)

