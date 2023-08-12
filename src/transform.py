import argparse

from lib.flight_transformer import FlightTransformer

parser = argparse.ArgumentParser(
    description=("Pass an unique experiment ID correlate pipeline components")
)
parser.add_argument("--experiment-id", required=True)

args = parser.parse_args()

transformer = FlightTransformer(
    "flight-delay-prediction", experiment_id=args.experiment_id
)
df = transformer.transform()
transformer.upload(df)
