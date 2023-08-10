import json
import os

import httpx
from dotenv import load_dotenv

from models import Flights

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
print(data)
obj = Flights(**data)
print(data["flights"][0])
print(len(data["flights"][0]))
