import os
import time
from dataclasses import dataclass

import httpx
from dotenv import load_dotenv

from src.logger import setup_logger
from src.models import Flight
from src.storage_manager import StorageManager

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


@dataclass
class Stats:
    n_downloaded: int
    n_uploaded: int

    def increment_downloads(self):
        self.n_downloaded += 1

    def increment_uploads(self):
        self.n_uploaded += 1


class FlightDataManager:
    def __init__(
        self, flights_client: FlightsClient, storage_client: StorageManager
    ) -> None:
        self.flights_client = flights_client
        self.storage_client = storage_client
        self.data = []
        self.stats = Stats()

    def get_all_flights(self) -> None:
        flights_iterator = PaginatedRequestsIterator("flights", self.flights_client)

        for page in flights_iterator:
            flights = page["flights"]
            for flight in flights:
                self.data.append(Flight(**flight))
                self.stats.increment_downloads()

        logger.info(f"Fetched {self.stats.n_downloaded} flights")

        return self.data

    def upload_all(self) -> None:
        for flight in self.data:
            self.storage_client.upload(flight.json(), f"raw_flights/{flight.id}")
            self.stats.increment_uploads()

        logger.info(f"Stored {self.stats.n_uploaded} flights")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} with {len(self.data)} flights"
