import time
from .send_data import send_list_message, send_text
from .spotify import Spotify

spotify = Spotify()


def ping():
    start_time = time.time()

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
    send_list_message(chat_id, message_id, title, possible_tracks)