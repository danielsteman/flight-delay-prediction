import argparse

from lib.flight_delay_model import FlightDelayModel
from lib.logger import setup_logger
from lib.storage_manager import StorageManager

logger = setup_logger()

"""
features: checkinAllocations,codeshares,flightDirection,terminal,transferPositions
"""

parser = argparse.ArgumentParser(
    description=(
        "Perform inference using a specific model by providing the experiment ID."
        "\n"
        "Usage example: inference.py --experiment_id <ID> --features <comma-separated"
        "values>"
    )
)

parser.add_argument("--experiment-id", required=True)
parser.add_argument("--features", required=True)
args = parser.parse_args()

storage_manager = StorageManager("flight-delay-prediction")

model = FlightDelayModel("flight-delay-prediction", args.experiment_id)


def parse_features(features):
    data = features.split(",")
    numeric_data = [float(i) for i in data]
    return [numeric_data]


fresh_flight_data = parse_features(args.features)
logger.info(f"Predicted flight delay in seconds: {model.infer(fresh_flight_data)}")
