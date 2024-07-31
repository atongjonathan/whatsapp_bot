import logging
import datetime
import pytz
# from app.services.openai_service import generate_response
import re
from .send_data import send_text, mark_as_read,  send_song, get_downloaded_url, send_artist
from .bot import ping, search_song, search_artist
from .spotify import Spotify
import os

TG_API_URL = os.environ.get("TG_API_URL")
spotify = Spotify()
help = {
    # command description used in the "help" command
    'start': 'Starts the bot',
    'help': 'Gives you information about the available commands',
    'song': 'Search for a song. Send the song title with the artist separated by a "-"',
    'artist': 'Search for an artist',
    'trending': 'Get hits of the week',
    'snippet': 'Listen to part of the song',
    'ping': "Check if I'm alive"
}
commands = [f"/{key}" for (key, value) in help.items()]
help_text = "The following commands are available: \n\n"
for key in commands:  # generate help text out of the commands dictionary defined at the top
    help_text += f"`{key}`" + ": "
    help_text += help[key.replace("/", "")] + "\n"
help_text += """
Example usage:
/artist Burna Boy
/song Closer - Halsey
/trending 10 - Get top 10 trending songs on Billboard Top 100
/snippet Closer - Halsey : Get 30 second preview of the song

*Note*: Songs will be sent in less than a minute depending on server speeds
    """

link_regex = "(https?:\\/\\/)?(www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{2,256}\\.[a-z]{2,6}\\b([-a-zA-Z0-9@:%_\\+.~#?&//=]*)?"
welcome_text = "Welcome to to Spotify SG✨'s bot!. \nText: `/help` to know how to use me!"


def convert_time(timestamp):
    utc_time = datetime.datetime.utcfromtimestamp(int(timestamp))
    east_africa_timezone = pytz.timezone('Africa/Nairobi')
    eat_time = utc_time.replace(
        tzinfo=pytz.utc).astimezone(east_africa_timezone)
    return eat_time.strftime('%Y-%m-%d %H:%M:%S')


def process_text_for_whatsapp(text):
    # Remove brackets
    pattern = r"\【.*?\】"
    # Substitute the pattern with an empty string
    text = re.sub(pattern, "", text).strip()

    # Pattern to find double asterisks including the word(s) in between
    pattern = r"\*\*(.*?)\*\*"

    # Replacement pattern with single asterisks
    replacement = r"*\1*"

    # Substitute occurrences of the pattern with the replacement
    whatsapp_style_text = re.sub(pattern, replacement, text)

    return whatsapp_style_text



def process_whatsapp_message(body):
    number = body["entry"][0]["changes"][0]["value"]["contacts"][0]["wa_id"]
    name = body["entry"][0]["changes"][0]["value"]["contacts"][0]["profile"]["name"]

    message = body["entry"][0]["changes"][0]["value"]["messages"][0]
    message_type = message.get("type")
    timestamp = message.get("timestamp")
    message_id = message.get("id")
    logging.info(
        f"Incoming {message_type} message from {name}, phone number: {number} at {convert_time(timestamp)} id: {message_id}")
    mark_as_read(message_id)
    chat_id = message.get("from")
    logging.info(message_id)
    if message_type == "text":
        text = message["text"]["body"]
        if bool(re.match(link_regex, text)):
            mini_link = text.split("spotify.com/")[1].split("?")[0]
            uri = mini_link.split("/")[1]
            track_details = spotify.get_chosen_song(uri)
            title = track_details["name"]
            performer = ', '.join(track_details["artists"])
            tg_link = get_downloaded_url(text, title, performer)
            send_song(tg_link, uri, chat_id, message_id)
            return
        queries = text.strip().split(" ")
        if queries[0] in commands:
            command = queries[0]
            if command == "/ping":
                send_text(chat_id, ping(), message_id)
            elif command == "/help":
                send_text(chat_id, help_text, message_id)
            elif command == "/start":
                send_text(chat_id, welcome_text, message_id)
            else:
                length = len(queries)
                if length > 1:
                    if command == "/song":
                        search_song(" ".join(queries[1:]), chat_id, message_id)
                    elif command == "/artist":
                        search_artist(" ".join(queries[1:]), chat_id, message_id)
                else:
                    send_text(chat_id, help_text, message_id)
    elif message_type == "interactive":
        try:
            uri = message["interactive"]["list_reply"]["id"] # Single Song or Artist
        except Exception:
            uri = message["interactive"]["button_reply"]["id"] # Artists PlayList
            send_text(chat_id, uri, message_id)
            return
        logging.info(uri)
        if 'artist' in uri:
            send_artist(uri, chat_id, message_id)
            return
        track_details = spotify.get_chosen_song(uri)
        title = track_details["name"]
        performer = ', '.join(track_details["artists"])
        tg_link = get_downloaded_url(track_details["external_url"], title, performer)
        send_song(tg_link, uri, chat_id, message_id)
        return


def is_valid_whatsapp_message(body):
    """
    Check if the incoming webhook event has a valid WhatsApp message structure.
    """
    return (
        body.get("object")
        and body.get("entry")
        and body["entry"][0].get("changes")
        and body["entry"][0]["changes"][0].get("value")
        and body["entry"][0]["changes"][0]["value"].get("messages")
        and body["entry"][0]["changes"][0]["value"]["messages"][0]
    )
