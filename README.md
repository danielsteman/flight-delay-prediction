# flight-delay-prediction

Flight delay prediction data engineering experiment.

## Plan of approach

### Extract

- [ ] Extract flight data through the [Schiphol PublicFlight API](https://developer.schiphol.nl/apis/flight-api/v4/flights?version=latest)

### Transform

- [ ] Find relevant features to predict flight delay

### Load

- [ ] Store train set on cloud storage

### Machine learning

- [ ] Create a simple model that predicts flight delay

## Docs

### Data models

`pydantic` models are generated with `datamodel-codegen` based on the OpenAPI Swagger doc provided by Schiphol PublicFlight API.

```
datamodel-codegen --target-python-version 3.10 --url "https://developer.schiphol.nl/swagger/spec/public-flights-v4.json" --output models.py --use-title-as-name
```
