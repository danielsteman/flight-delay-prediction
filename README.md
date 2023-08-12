# flight-delay-prediction ✈️

Flight delay prediction data engineering experiment.

## Plan of approach 📝

### Extract 🔍

- [x] Extract flight data through the [Schiphol PublicFlight API](https://developer.schiphol.nl/apis/flight-api/v4/flights?version=latest)
- [x] Store in Google storage bucket

### Transform 🔀

- [x] Load from Google storage bucket
- [x] Find relevant features to predict flight delay
- [x] Store in Google storage bucket

### Machine learning 🤖

- [x] Load train set from Google storage bucket
- [ ] Train a simple model that predicts flight delay
- [ ] Serialize and store model in Google storage bucket
- [ ] Run inference service

## Docs

### Authentication 🔒

In development, you might want to add these [Schiphol PublicFlight API](https://developer.schiphol.nl/apis/flight-api/v4/flights?version=latest) credentials to `.env`. They also exist as Github secrets.

```
API_KEY
API_ID
```

The application uses a Google Storage Bucket and authenticates with a service account. Credentials are expected in `/gcp-credentials.json`.

### Run locally 🚀

Extract data:

```
python src/extract
```

Set an experiment ID and transform data:

```
export EXPERIMENT_ID=$(python -c "import uuid; print(uuid.uuid4())")
python src/transform.py --experiment-id $EXPERIMENT_ID
```

### Build Docker images 📦

```
docker build -t flight-delay-prediction-extract -f Dockerfile.extract .
docker build -t flight-delay-prediction-transform -f Dockerfile.transform .
docker build -t flight-delay-prediction-train -f Dockerfile.train .
```

### Data models 👠

`pydantic` models are generated with `datamodel-codegen` based on the OpenAPI Swagger doc provided by Schiphol PublicFlight API. `datamodel-codegen` can parse json directly through the download link of the [Swagger document](https://swagger.io/specification/).

```

datamodel-codegen --target-python-version 3.10 --url "https://developer.schiphol.nl/swagger/spec/public-flights-v4.json" --output models.py --use-title-as-name

```

Because we don't need all models, it's also possible to extract a part of the definition, safe it as a Python dict (`data/flight.py` e.g.) and parse that to generate models.

```

datamodel-codegen --input-file-type dict --output models.py --target-python-version 3.10 --input data/flight.py

```

I like using code generation tools for schemas because it's a less error prone method than doing it manually.

## Next steps ➡️

- [ ] Refactor Poetry dependencies to make Docker images "leaner"

## Contribute 🤝

Install dependencies and `pre-commit` hooks, otherwise the CI will complain to you 😤.

```
poetry install
pre-commit install

```
