# MP2: Data Processing API

DS3500 mini-project: build a REST API with FastAPI across two parts.

## Setup

Run these commands from the project root:

```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
```

## Project structure

```text
mp2-rest-api/
├── .gitignore
├── README.md
├── requirements.txt
├── main.py
├── src/
│   ├── __init__.py
│   ├── models.py
│   ├── storage.py
│   └── utils.py
├── fixtures/
│   └── .gitkeep
└── tests/
    ├── test_api.py
    └── test_storage.py
```

## Current progress

The project structure and dependencies are set up. The health and dataset
metadata response models are defined, and MP1's logging configuration is reused
with INFO output by default and DEBUG output when verbose mode is enabled.

In-memory dataset storage supports sequential IDs, defensive DataFrame copies,
metadata calculated from current data, updates, and clearing all datasets.
Stored data is lost when the process stops.

The health, CSV upload, and dataset retrieval endpoints are implemented.
The sample dataset and a manual testing walkthrough will be added next.

## Run the API

With the virtual environment activated, run:

```bash
python -m uvicorn main:app --reload
```

Open http://127.0.0.1:8000/docs for the interactive API documentation.

| Endpoint | Behavior |
| --- | --- |
| `GET /health` | Return application status and version. |
| `POST /upload` | Accept a CSV file and return dataset metadata. |
| `GET /datasets/{dataset_id}?limit=2` | Return up to two rows and the full dataset row count. |

Retrieval defaults to 100 rows. Unsupported or unreadable uploads return 400,
missing datasets return 404, and invalid parameters such as `limit=0` return 422.

## Tests

```bash
python -m pytest -q
```

Storage tests in `tests/test_storage.py` cover ID assignment, copy isolation,
updated metadata, missing IDs, clearing storage, and DEBUG logging.
API tests in `tests/test_api.py` cover the endpoints, upload errors, row limits,
row order, missing values, and retrieval without changing stored data.
