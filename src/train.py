import argparse

from lib.storage_manager import StorageManager

parser = argparse.ArgumentParser(
    description=("Pass an unique experiment ID correlate pipeline components")
)
parser.add_argument("--experiment-id")

args = parser.parse_args()

storage_manager = StorageManager("flight-delay-prediction")
storage_manager.download(f"{args.experiment_id}/train_set.parquet")
