import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()
MONGODB_CREDENTIALS = os.environ.get("MONGODB_CREDENTIALS")

headersList = {
    "Accept": "*/*",
    "Content-Type": "application/json"
}


payload = json.dumps(json.loads(MONGODB_CREDENTIALS))
reqUrl = "https://eu-west-2.aws.services.cloud.mongodb.com/api/client/v2.0/app/data-kmyiqtw/auth/providers/local-userpass/login"
response = requests.request("POST", reqUrl, data=payload,  headers=headersList)

access_token = response["access_token"]


reqUrl = "https://eu-west-2.aws.data.mongodb-api.com/app/data-kmyiqtw/endpoint/data/v1/action/findOne"

headersList = {
    "Accept": "*/*",
    "Content-Type": "application/json",
    "Access-Control-Request-Headers": "*/*",
    "Authorization": f"Bearer {access_token}"
}


def search_db(title, performer):
    payload = json.dumps({
        "collection": "songs",
        "database": "sgbot",
        "dataSource": "Cluster0",
        "filter": {
            "title": title,
            "performer": performer
        }
    })

    response = requests.request(
        "POST", reqUrl, data=payload,  headers=headersList)
    return response.json()


print(response.text)
