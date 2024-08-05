import requests
import os
import logging
# from urllib.parse import quote


TG_API_URL = os.environ.get("TG_API_URL")

headersList = {
    "Accept": "*/*",
    "Content-Type": "application/json"
}


def search_db(title, performer, doc=None):
    if doc:
        reqUrl = f"{TG_API_URL}/whatsapp"
        response = requests.request(
            "POST", reqUrl, data=doc,  headers=headersList)
        return bool(response.json()["response"])
    else:
        reqUrl = f"{TG_API_URL}/?title={title}&performer={performer}"
        payload = ""
        response = requests.request(
            "POST", reqUrl, data=payload,  headers=headersList)
        return response.json()["response"]

def insert_doc(doc:dict):
    reqUrl = f"{TG_API_URL}/whatsapp"
    response = requests.request(
        "GET", reqUrl, data="",  headers=headersList, params=doc)
    return response.json()["response"]


def delete_doc(document):
    reqUrl = f"{TG_API_URL}/"
    response = requests.request(
        "DELETE", reqUrl, data=document,  headers=headersList)
    return response.json()["response"]


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
