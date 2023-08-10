import json
import os

import httpx
from dotenv import load_dotenv
from logger import setup_logger
from models import Flight
import time

load_dotenv()
logger = setup_logger()


class FlightsClient(httpx.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_headers = {
            "Accept": "application/json",
            "app_id": os.environ["API_ID"],
            "app_key": os.environ["API_KEY"],
            "ResourceVersion": "v4",
        }
        self.base_url = "https://api.schiphol.nl/public-flights"
        self.retries = kwargs.get("retries", 3)

    def request(self, endpoint: str, method: str = "GET", *args, **kwargs):
        headers = kwargs.get("headers")
        if not headers:
            headers = {}
        merged_headers = {**self.default_headers, **headers}
        kwargs["headers"] = merged_headers
        attempts = 0
        while attempts <= self.retries:
            res = super().request(method, f"{self.base_url}{endpoint}", *args, **kwargs)
            if res.status_code == 429:
                retry_after = float(res.headers.get("Retry-After", 0.5))
                logger.warning(
                    f"Hit rate limit, waiting for {retry_after} seconds before retrying"
                )
                time.sleep(retry_after)
            else:
                return res


class PaginatedRequestsIterator:
    BASE_URL = "https://api.schiphol.nl:443/public-flights/"

    def __init__(self, endpoint: str, client: httpx.Client) -> None:
        self.endpoint = endpoint
        self.client = client
        self.next_url = endpoint

    def __iter__(self):
        return self

    def __next__(self):
        if not self.next_url:
            raise StopIteration

        endpoint = self._remove_base(self.next_url)

        try:
            response = self.client.request(endpoint=endpoint)
            response.raise_for_status()

            logger.info(f"Fetched data from {endpoint}")
        except httpx.HTTPStatusError as exc:
            logger.error(f"Request failed with status code {exc.response.status_code}")
            logger.error("Response content:", exc.response.text)

        data = response.json()

        self.next_url = response.links.get("next", {}).get("url")

        return data

    @staticmethod
    def _remove_base(url: str) -> str:
        return url.removeprefix(PaginatedRequestsIterator.BASE_URL)


class FlightDataManager:
    def __init__(self) -> None:
        self.client = FlightsClient()


# flights_iterator = PaginatedRequestsIterator("flights?page=230", FlightsClient())

# flights = []
# for flight_data in flights_iterator:
#     flights.append(flight_data)

# for flight in flights:
#     obj = Flight(**flights)
