from lib.flight_transformer import FlightTransformer

transformer = FlightTransformer("flight-delay-prediction")
df = transformer.transform()
transformer.upload(df)
