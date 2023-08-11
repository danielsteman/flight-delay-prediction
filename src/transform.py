import json
from typing import Dict

import joblib

from src.logger import setup_logger
from src.storage_manager import StorageManager
from src.utils import filter_nested_dict

logger = setup_logger()


def get_data() -> None:
    manager = StorageManager("flight-delay-prediction")
    flights = manager.download_all("raw_flights")
    manager.save_locally(flights, "raw_flights")


def parse_and_extract(data: str) -> Dict:
    keys_to_extract = [
        "expectedTimeGateClosing",
        "scheduleDateTime",
        "aircraftType",
        "codeshares",
        "flightDirection",
        "transferPositions",
        "checkinAllocations",
        "terminal",
    ]
    extracted_data = filter_nested_dict(
        json.loads(data), keys_to_include=keys_to_extract
    )
    return extracted_data


def make_tabular(data: Dict) -> Dict:
    tabular_data = data
    tabular_data["aircraftType"] = data.get("aircraftType")
    tabular_data["codeshares"] = (
        len(data["codeshares"]["codeshares"]) if data["codeshares"] else 0
    )
    tabular_data["transferPositions"] = (
        data["transferPositions"]["transferPositions"][0]
        if data["transferPositions"]
        else 0
    )
    tabular_data["checkinAllocations"] = (
        len(data["checkinAllocations"]["checkinAllocations"])
        if data["checkinAllocations"]
        else 0
    )
    return tabular_data


def transform():
    json_flights = joblib.load("data/raw_flights.joblib")

    logger.info(f"Number of flights: {len(json_flights)}")

    tabular_flights = []

    for flight in json_flights:
        dict_flight = parse_and_extract(flight)
        tabular_flight = make_tabular(dict_flight)
        tabular_flights.append(tabular_flight)
