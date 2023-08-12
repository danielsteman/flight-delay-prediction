import argparse

from lib.flight_delay_model import FlightDelayModel
from lib.storage_manager import StorageManager

parser = argparse.ArgumentParser(
    description=("Pass an unique experiment ID correlate pipeline components")
)
parser.add_argument("--experiment-id", required=True)
args = parser.parse_args()

storage_manager = StorageManager("flight-delay-prediction")

model = FlightDelayModel("flight-delay-prediction", args.experiment_id)
model.train()
