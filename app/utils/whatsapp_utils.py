import logging
import datetime
import pytz
# from app.services.openai_service import generate_response
import re
# from .send_data import send_text, mark_as_read


help = {
    # command description used in the "help" command
    'start': 'Get used to the bot',
    'help': 'Gives you information about the available commands',
    'song': 'Search for a song',
    'artist': 'Search for an artist',
    'trending': 'Get hits of the week',
    'snippet': 'Listen to part of the song',
    'ping': 'Test me'
}
commands = [key for (key, value) in help.items()]
help_text = "The following commands are available: \n\n"
for key in commands:  # generate help text out of the commands dictionary defined at the top
    help_text += "/" + key + ": "
    help_text += help[key] + "\n"
help_text += """
Example usage:
/artist Burna Boy or /artist only and reply with the name
/song Closer - Halsey  or /song only and reply with the name
/trending 10 - Get top 10 trending songs on Billboard Top 100
/snippet Closer - Halsey : Get 30 second preview of the song
    """

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
    message_type = message.get("type")
    message_id = message.get("id")
    chat_id = message.get("from")
    if message_type == "text":
        text = message["text"]["body"].strip()
        text_list = [word for word in text]
        if text_list[0] in commands:
            send_text(chat_id, help_text, message_id)



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
