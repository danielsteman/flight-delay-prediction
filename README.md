# flight-delay-prediction ✈️

Flight delay prediction data engineering experiment. The goal is to retrieve data from the [Schiphol PublicFlight API](https://developer.schiphol.nl/apis/flight-api/v4/flights?version=latest), pick features and predict flight delay.

This project is divided into distinct phases: fetching flight data from a public API, refining and selecting relevant information, and training a model using the refined data. The goal is to establish a modular pipeline, where each step can be reused independently. Testing is carried out separately for each stage to ensure that modifications in one stage do not impact the others. Additionally, the project includes the ability to make predictions using fresh flight data, which could potentially be offered through an API in a future update.

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
- [x] Train a simple model that predicts flight delay
- [x] Serialize and store model in Google storage bucket
- [x] Run inference

## Docs

### Authentication 🔒

In development, you need to add these [Schiphol PublicFlight API](https://developer.schiphol.nl/apis/flight-api/v4/flights?version=latest) credentials to `.env`. They also exist as Github secrets.

```
API_KEY
API_ID
```

The application uses a Google Storage Bucket and authenticates with a service account. Credentials are expected in `/gcp-credentials.json`.

### Run locally 🚀

Extract data:

```
python src/extract.py
```

Set a random experiment ID and transform data:

```
export EXPERIMENT_ID=$(python -c "import uuid; print(uuid.uuid4())")
python src/transform.py --experiment-id $EXPERIMENT_ID
```

Use the same experiment ID to train the model on the data you just transformed:

```
python src/train.py --experiment-id $EXPERIMENT_ID
```

Pass new flight data to the newly trained model:

```
python src/inference.py --experiment-id $EXPERIMENT_ID --features 1,1,1,1,1
>>> Predicted flight delay in seconds: [889.9810475]
```

### Build Docker images 📦

Secrets need to be passed at runtime. Although it's possible to pass them at build time, this seemed safer and provides flexibility. Something like HashiCorp Vault's "secrets injection" is the real solution here.

Build images:

```
docker build -t flight-delay-prediction-extract -f Dockerfile.extract .
docker build -t flight-delay-prediction-transform -f Dockerfile.transform .
docker build -t flight-delay-prediction-train -f Dockerfile.train .
```

Run images:

```
docker run -e API_KEY=myapikey -e API_ID=myappid -it flight-delay-prediction-extract
docker run -it flight-delay-prediction-transform --experiment-id $EXPERIMENT_ID
docker run -it flight-delay-prediction-train --experiment-id $EXPERIMENT_ID
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

- [ ] Add more tests
- [ ] Build and push Docker images from CI pipeline
- [ ] Refactor Poetry dependencies to make Docker images "leaner"
- [ ] Create Docker base image
- [ ] Expose an inference endpoint (with FastAPI for example) such that it can be integrated in other business processes
- [ ] Create Airflow DAG(s) to schedule Docker containers and to automate extraction, transformation, loading and model training
- [ ] Integrate a tool for secrets injection (such as [HashiCorp Vault](https://www.vaultproject.io/))

## Contribute 🤝

Install dependencies and `pre-commit` hooks, otherwise the CI will complain 😤.

```
poetry shell
poetry install
pre-commit install
```

Run unit tests:

```
pytest -s -vv
```
