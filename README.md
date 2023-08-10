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

`pydantic` models are generated with `datamodel-codegen` based on the OpenAPI Swagger doc provided by Schiphol PublicFlight API. `datamodel-codegen` can parse json directly through the download link of the [Swagger document](https://swagger.io/specification/).

```
datamodel-codegen --target-python-version 3.10 --url "https://developer.schiphol.nl/swagger/spec/public-flights-v4.json" --output models.py --use-title-as-name
```

Because we don't need all models, it's also possible to extract a part of the definition, safe it as a Python dict (`data/flight.py` e.g.) and parse that to generate models.

```
datamodel-codegen --input-file-type dict --output models.py --target-python-version 3.10 --input data/flight.py
```

I like using code generation tools for schemas because it's a less error prone method than doing it manually.
