import logging
import time
from .send_data import send_song_list_message, send_text, send_artist_list_message, send_trailers_list_message
from .spotify import Spotify
from datetime import datetime
import requests

spotify = Spotify()


def ping(timestamp):
    start_time = time.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
    start_time = time.mktime(start_time)
    end_time = time.time()
    elapsed_time_ms = int((end_time - start_time) * 1000)
    return f"Pong! 🏓\nResponse Time: `{elapsed_time_ms} ms`"


def check_input(text):
    """
    Extracts the artist and song from the string provided.

    Args:
        message: Message object from Telegram containing the user input.

    Returns:
        Tuple of (artist, title) if successful, otherwise sends an error message.
    """
    if "-" not in text:
        text += " - "

    data_list = text.split("-")
    title = data_list[0].strip()
    artist = data_list[1].strip() if len(data_list) > 1 else ""
    return artist, title


def search_song(text, chat_id, message_id):
    try:
        artist, title = check_input(text)
    except Exception:
        return
    possible_tracks = spotify.song(artist, title)
    no_of_results = len(possible_tracks)
    NO_RESULTS_MESSAGE = f"`{title}` not found!⚠. Please check your spelling and also include special characters"
    if no_of_results == 0:
        send_text(chat_id, NO_RESULTS_MESSAGE, message_id)
        return
    send_song_list_message(chat_id, message_id, title, possible_tracks)


def search_artist(text, chat_id, message_id):
    possible_artists = spotify.artist(text)
    no_of_results = len(possible_artists)
    NO_RESULTS_MESSAGE = f"`{text}` not found!⚠. Please check your spelling and also include special characters"
    if no_of_results == 0:
        send_text(chat_id, NO_RESULTS_MESSAGE, message_id)
        return
    send_artist_list_message(chat_id, message_id, text, possible_artists)


def search_trailer(text, chat_id, message_id):
    logging.info("Searching trailer, ", text)
    reqUrl = f"https://itunes.apple.com/search?term={text}&entity=movie&media=movie"
    response = requests.get(reqUrl)
    data = response.json()
    results = data.get("results")
    if not results:
        NO_RESULTS_MESSAGE = f"`{text}` results not found!⚠"
        logging.info(NO_RESULTS_MESSAGE)
        return send_text(chat_id, NO_RESULTS_MESSAGE, message_id)
    if len(results) == 0:
        NO_TRAILERS_MESSAGE = f"`No trailers of {text}` were found!⚠. Please check your spelling and also include special characters"
        logging.info(NO_TRAILERS_MESSAGE)
        return send_text(chat_id, NO_TRAILERS_MESSAGE, message_id)
    send_trailers_list_message(chat_id, message_id, results)
