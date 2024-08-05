import logging
from flask import jsonify
import os
import requests
import json
import telebot
from .spotify import Spotify
from .database import search_db, get_url_from_api, delete_doc
import time
from urllib.parse import quote

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


def get_downloaded_url(spotify_url, title, performer):
    response = search_db(quote(title), quote(performer))
    document = response["document"]
    try:
        file_info = bot.get_file(document["file_id"])
        url = 'https://api.telegram.org/file/bot{0}/{1}'.format(
            TELEGRAM_BOT_TOKEN, file_info.file_path)
    except Exception as e:
        logging.error(
            f"Getting file_info url failed: {e}: {document}")
        response = delete_doc(document)
        logging.info(response)
        url = get_url_from_api(spotify_url)
    return url


def mark_as_read(message_id):
    body = json.dumps(
        {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id
        })
    try:
        response = requests.post(
            url, data=body, headers=headers)
        response.raise_for_status()
        return jsonify({"status": "Marked", "message": f"message:{message_id} marked as read"}), 200
    except requests.Timeout as e:
        logging.error(e)
        return jsonify({"status": "error", "message": "Failed to mark message as read"}), 500


def call_api(message_body):
    message_body = json.dumps(message_body)
    response = requests.post(
        url, data=message_body, headers=headers)
    if response.ok:
        return
    elif response.status_code == 400:
        time.sleep(3)
        call_api(message_body)
    else:
        logging.error(
            f"Error occurred while sending {message_body}: {response.status_code}, {response.reason}")
    return


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
            "body": str(text)
        }
    }
    call_api(body)


def send_document(chat_id, link, message_id, file_name, caption=None):
    if not link:
        return
    body = {
        "messaging_product": "whatsapp",
        "context": {
            "message_id": message_id
        },
        "to": chat_id,
        "type": "document",
        "document": {
            "link": link,
            "filename": f"{file_name}.mp3",
        }
    }
    if caption:
        body["document"]["caption"] = caption
    call_api(body)


def send_audio(chat_id, link, message_id):
    if not link:
        return
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


def send_song_list_message(chat_id, message_id, title, results):
    if not results:
        return
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
                "text": f"Song results for `{title}`👇"
            },
            "action": {
                "button": "Song Results",
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
    if not results:
        return
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
                "text": f"Artist results for `{title}` 👇 "
            },
            "action": {
                "button": "Artist Results",
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


def send_albums_list_message(chat_id, message_id, title, results):
    if not results:
        return
    rows = [{
        "id": result["uri"],
        "title": result["name"] if len(result["name"]) < 24 else result["name"][:21] + "-",
        "description": result["name"][21:72] if len(result["name"]) > 24 else ""
    } for result in results[:10]]
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
                "text": f"Here are the `{title}` results👇"
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
    if not link:
        return
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


def send_song(uri, chat_id, message_id):
    track_details = spotify.get_chosen_song(uri)
    title = track_details["name"]
    performer = ', '.join(track_details["artists"])
    duration = track_details["duration_ms"]
    minutes = duration // 60000
    seconds = int((duration % 60000) / 1000)
    caption = f'👤Artist: `{performer}`\n🎵Song : `{title}`\n━━━━━━━━━━━━\n📀Album : `{track_details["album"]}`\n🔢Track : {track_details["track_no"]} of {track_details["total_tracks"]}\n⭐️ Released: `{track_details["release_date"]}`\n⌚Duration: `{minutes}:{seconds}`\n🔞Is Explicit: {track_details["explicit"]}\n'
    send_photo(chat_id, track_details["image"], caption, message_id)
    file_name = f'{performer} - {title}'
    tg_link = get_downloaded_url(
        track_details["external_url"], title, performer)
    send_document(chat_id, tg_link, message_id, file_name)
    time.sleep(2)
    # completed_text = f"{file_name} sent successfully. 💪!"
    # send_text(chat_id, completed_text, message_id)


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


def send_album(uri, chat_id, message_id):
    album_details = spotify.album("", "", uri)
    caption = f'👤Artist: `{", ".join(album_details["artists"])}`\n📀 Album: `{album_details["name"]}`\n⭐️ Released: `{album_details["release_date"]}`\n🔢 Total Tracks: {album_details["total_tracks"]}'
    send_photo(chat_id, album_details["images"], caption, message_id)
    album_tracks = album_details['album_tracks']
    for track in album_tracks:
        uri = track["uri"]
        track_details = spotify.get_chosen_song(uri)
        title = track_details["name"]
        performer = ', '.join(track_details["artists"])
        file_name = f'{performer} - {title}'
        try:
            tg_link = get_downloaded_url(
                track_details["external_url"], title, performer)
            caption = f"🔢Track no : {track_details['track_no']} of {track_details['total_tracks']}"
            send_document(chat_id, tg_link, message_id, file_name, caption)
        except Exception as e:
            logging.info(f"Failed to get send {track_details['name']}: {e}")
            return
    text = f'Those are all the {track_details["total_tracks"]} track(s) in "`{album_details["name"]}`" by `{", ".join(album_details["artists"])}`. 💪!',
    # send_text(chat_id, text, message_id)
