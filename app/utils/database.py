import requests
import os
import logging
import json
from dotenv import load_dotenv
# from urllib.parse import quote

load_dotenv()


TG_API_URL = os.environ.get("TG_API_URL")
DATA_API_URL = "https://eu-west-2.aws.data.mongodb-api.com/app/data-kmyiqtw/endpoint/data/v1/action/"

headersList = {
    "Accept": "*/*",
    "Content-Type": "application/json",
    "Access-Control-Request-Headers": "*/*",

}


def apiToken():
    response = requests.request(
        "GET", TG_API_URL, data="",  headers=headersList)

    return response.json()["response"]["access_token"]


def search_db(title, performer, doc=None):
    reqUrl = f"{DATA_API_URL}findOne"
    api_key = apiToken()
    headersList["Authorization"] = f"Bearer {api_key}"
    body = {
        "database": "sgbot",
        "dataSource": "Cluster0"
    }
    if doc:
        logging.info(f"Searching for: {doc}")
        body["collection"] = "whatsapp"
        body["filter"] = doc
        payload = json.dumps(body)
        response = requests.request(
            "POST", reqUrl, data=payload,  headers=headersList)
        return response.json()
    body["collection"] = "songs"
    body["filter"] = {
        "title": title,
        "performer": performer
    }
    payload = json.dumps(body)
    response = requests.request(
        "POST", reqUrl, data=payload,  headers=headersList)
    return response.json()


def insert_doc(doc: dict):
    reqUrl = f"{DATA_API_URL}insertOne"
    api_key = apiToken()
    headersList["Authorization"] = f"Bearer {api_key}"

    payload = json.dumps({
        "collection": "whatsapp",
        "database": "sgbot",
        "dataSource": "Cluster0",
        "document": doc
    })

    response = requests.request(
        "POST", reqUrl, data=payload,  headers=headersList)
    return response.json()


def delete_doc(document):
    reqUrl = f"{DATA_API_URL}deleteOne"
    api_key = apiToken()
    headersList["Authorization"] = f"Bearer {api_key}"

    payload = json.dumps({
        "collection": "whatsapp",
        "database": "sgbot",
        "dataSource": "Cluster0",
        "document": document
    })
    response = requests.request(
        "POST", reqUrl, data=payload,  headers=headersList)
    return response.json()


def get_url_from_api(spotify_url):
    reqUrl = f"{TG_API_URL}?track_url={spotify_url}"
    try:
        response = requests.request("POST", reqUrl, headers=headersList)
        data = response.json()
        url = data["response"]["url"]
        return url
    except Exception as e:
        logging.error(f"Api call failed: {e}")
        return

