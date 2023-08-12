from lib.flight_transformer import FlightTransformer

transformer = FlightTransformer("flight-delay-prediction")
df = transformer.transform()

print(df)

# transformer.upload(df)
