import argparse

import pandas as pd

from lib.enums import ContentType
from lib.storage_manager import StorageManager

parser = argparse.ArgumentParser(
    description=("Pass an unique experiment ID correlate pipeline components")
)
parser.add_argument("--experiment-id", required=True)

args = parser.parse_args()

storage_manager = StorageManager("flight-delay-prediction")
data = storage_manager.download(
    f"experiments/experiment_{args.experiment_id}/transformed_flights.parquet",
    content_type=ContentType.STREAM,
)
df = pd.read_parquet(data)

independent_var = "delay_in_seconds"
y = df[independent_var]
X = df.drop(columns=[independent_var])
