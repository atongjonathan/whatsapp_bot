import logging
from flask import jsonify
import os
import requests
import json
import telebot
from .spotify import Spotify

spotify = Spotify()

ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
VERSION = os.environ.get("VERSION")
headers = {
    "Content-type": "application/json",
    "Authorization": f"Bearer {ACCESS_TOKEN}",
}
headersList = {
    "Accept": "*/*",
    "Content-Type": "application/json"
}
url = f"https://graph.facebook.com/{VERSION}/{PHONE_NUMBER_ID}/messages"
message_body = json.dumps(
    {
        "messaging_product": "whatsapp",
        "context": ""
    })
TG_API_URL = os.environ.get("TG_API_URL")


def get_downloaded_url(spotify_url, title, performer):
    response = search_db(title, performer)
    document = response["document"]
    logging.info(f"Document: {document}")
    if document:
        file_info = bot.get_file(document["file_id"])
        url = 'https://api.telegram.org/file/bot{0}/{1}'.format(
            TELEGRAM_BOT_TOKEN, file_info.file_path)
    else:
        reqUrl = f"{TG_API_URL}?track_url={spotify_url}"
        response = requests.request("GET", reqUrl, headers=headersList)
        data = response.json()
        url = data["response"]["url"]
    print(url)
    return url


def search_db(title, performer):
    reqUrl = f"{TG_API_URL}/?title={title}&performer={performer}"
    payload = ""
    response = requests.request(
        "POST", reqUrl, data=payload,  headers=headersList)
    return response.json()["response"]


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
        "to": chat_id,
        "type": "text",
        "text": {
            "preview_url": True,
            "body": text
        }
    }
    call_api(body)


def send_document(chat_id, link, message_id, file_name):
    body = {
        "messaging_product": "whatsapp",
        "context": {
            "message_id": message_id
        },
        "to": chat_id,
        "type": "document",
        "document": {
            "link": link,
            "filename": f"{file_name}.mp3"
        }
    }
    call_api(body)


def send_audio(chat_id, link, message_id):
    body = {
        "messaging_product": "whatsapp",
        "context": {
            "message_id": message_id
        },
        "to": chat_id,
        "type": "audio",
        "audio": {
            "link": link,
        }
    }
    call_api(body)


def send_list_message(chat_id, message_id, title, results):
    rows = [{
        "id": result["uri"],
        "title": result["artists"] if len(result["artists"]) < 24 else result["artists"][:21] + "...",
        "description": result["name"] if len(result["name"]) < 24 else result["name"][:69] + "..."
    } for result in results]
    body = {
        "messaging_product": "whatsapp",
        "context": {
            "message_id": message_id
        },
        "recipient_type": "individual",
        "to": chat_id,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "body": {
                "text": f"Here are your results for `{title}`👇"
            },
            "action": {
                "button": "View Results",
                "sections": [
                    {
                        "title": "Choose song",
                        "rows": rows
                    },
                ]
            }
        }
    }
    call_api(body)


def send_artist_list_message(chat_id, message_id, title, results):
    rows = [{
        "id": result["uri"],
        "title": result["name"] if len(result["name"]) < 24 else result["name"][:21] + "...",
        "description": result["followers"] + " followers"
    } for result in results]
    body = {
        "messaging_product": "whatsapp",
        "context": {
            "message_id": message_id
        },
        "recipient_type": "individual",
        "to": chat_id,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "body": {
                "text": f"Here are your results for `{title}`👇"
            },
            "action": {
                "button": "View Results",
                "sections": [
                    {
                        "title": "Choose artist",
                        "rows": rows
                    },
                ]
            }
        }
    }
    call_api(body)


def send_photo(chat_id, link, caption, message_id):
    body = {
        "messaging_product": "whatsapp",
        "to": chat_id,
        "context": {
            "message_id": message_id
        },
        "type": "image",
        "image": {
            "link": link,
            "caption": caption
        }
    }
    call_api(body)


def send_song(tg_link, uri, chat_id, message_id):
    track_details = spotify.get_chosen_song(uri)
    duration = track_details["duration_ms"]
    minutes = duration // 60000
    seconds = int((duration % 60000) / 1000)
    caption = f'👤Artist: `{", ".join(track_details["artists"])}`\n🎵Song : `{track_details["name"]}`\n━━━━━━━━━━━━\n📀Album : `{track_details["album"]}`\n🔢Track : {track_details["track_no"]} of {track_details["total_tracks"]}\n⭐️ Released: `{track_details["release_date"]}`\n⌚Duration: `{minutes}:{seconds}`\n🔞Is Explicit: {track_details["explicit"]}\n'
    send_photo(chat_id, track_details["image"], caption, message_id)
    file_name = f'{", ".join(track_details["artists"])} - {track_details["name"]}'
    send_document(chat_id, tg_link, message_id, file_name)


def send_artist(uri, chat_id, message_id):
    artist_details = spotify.get_chosen_artist(uri)
    lists_of_type = [
        artist_details["artist_singles"]["single"],
        artist_details["artist_albums"]["album"],
        artist_details["artist_compilations"]["compilation"]
    ]
    type = ['single', 'album', 'compilation']
    rows = []

    for idx, item in enumerate(lists_of_type):
        if (len(item) > 0):
            row = {
                "type": "reply",
                "reply": {
                    "id": f"{type[idx]}_{uri}",
                    "title": f"{type[idx].title()}s🧐"
                }
            }  # Make only when more than 0
            rows.append(row)
    caption = f'👤Artist: `{artist_details["name"]}`\n🧑Followers: `{artist_details["followers"]:,}` \n🎭Genre(s): `{", ".join(artist_details["genres"])}` \n'
    body = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": chat_id,
        "context": {
            "message_id": message_id
        },
        "type": "interactive",
        "interactive": {
                "type": "button",
                "header": {
                    "type": "image",
                    "image": {
                        "link": artist_details["images"]
                    }
                },
            "body": {
                    "text": caption
                    },
            "action": {
                    "buttons": rows
                    }
        }
    }
    call_api(body)
