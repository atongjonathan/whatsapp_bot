import logging
import datetime
import pytz
# from app.services.openai_service import generate_response
import re
from .send_data import send_message, mark_as_read


def convert_time(timestamp):
    utc_time = datetime.datetime.utcfromtimestamp(int(timestamp))
    east_africa_timezone = pytz.timezone('Africa/Nairobi')
    eat_time = utc_time.replace(tzinfo=pytz.utc).astimezone(east_africa_timezone)
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
    logging.info(f"Incoming {message_type} message from {name}, phone number: {number} at {convert_time(timestamp)} id: {message_id}")
    mark_as_read(message_id)
    send_message(message)


    # TODO: implement custom function here


    # OpenAI Integration
    # response = generate_response(message_body, wa_id, name)
    # response = process_text_for_whatsapp(response)





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
