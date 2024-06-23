import requests
import mimetypes
import os
from dotenv import load_dotenv

load_dotenv()

headersList = {
 "Accept": "*/*",
 "User-Agent": "Thunder Client (https://www.thunderclient.com)",
 "Authorization": f"Bearer {os.environ.get('ACCESS_TOKEN')}" 
}
file_path = "C:/Users/Administrator/Downloads/kill_bill_video.mp4"
mime_type, _ = mimetypes.guess_type(file_path)
if not mime_type:
    raise ValueError("Could not determine the MIME type of the file")
print(mime_type)
payload = ""
files = {
    'file': (file_path.split('/')[-1], open(file_path, 'rb'), mime_type),
    # 'type': (None, mime_type)
}
reqUrl = f"https://graph.facebook.com/{os.environ.get('VERSION')}/{os.environ.get('PHONE_NUMBER_ID')}/media?&messaging_product=whatsapp&type={mime_type}"

# Make the POST request to upload the file
response = requests.request("POST", reqUrl, data=payload,  headers=headersList, files=files)

print(response.text)