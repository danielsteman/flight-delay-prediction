import json
import os
from typing import Dict

import httpx
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ["API_KEY"]

url = "https://api.schiphol.nl/public-flights/flights"

headers = {
    "Accept": "application/json",
    "app_id": "5760df96",
    "app_key": api_key,
    "ResourceVersion": "v4",
}

res = httpx.get(url, headers=headers)
data = json.loads(res.content)


def get_open_api_spec(to_path: str = "data/public-flights-v4.json") -> Dict:
    openapi_spec_download_link = (
        "https://developer.schiphol.nl/swagger/spec/public-flights-v4.json"
    )
    res = httpx.get(openapi_spec_download_link)
    content = res.content
    data = json.loads(content)
    with open(to_path, "w") as file:
        json.dump(data, file, indent=4)
    return data
