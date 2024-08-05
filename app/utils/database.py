import requests
import os
import logging

TG_API_URL = os.environ.get("TG_API_URL")

headersList = {
    "Accept": "*/*",
    "Content-Type": "application/json"
}

def search_db(title, performer):
    reqUrl = f"{TG_API_URL}/?title={title}&performer={performer}"
    payload = ""
    response = requests.request(
        "POST", reqUrl, data=payload,  headers=headersList)
    return response.json()["response"]

def delete_doc():
    pass

def insert_doc():
    pass
def get_url_from_api(spotify_url):
    reqUrl = f"{TG_API_URL}?track_url={spotify_url}"
    try:
        response = requests.request("GET", reqUrl, headers=headersList)
        data = response.json()
        url = data["response"]["url"]
        return url
    except Exception as e:
        logging.error(f"Api call failed: {e}")
        return