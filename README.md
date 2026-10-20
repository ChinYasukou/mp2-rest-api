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
    └── test_storage.py
```

## Current progress

The project structure and dependencies are set up. The health and dataset
metadata response models are defined, and MP1's logging configuration is reused
with INFO output by default and DEBUG output when verbose mode is enabled.

In-memory dataset storage supports sequential IDs, defensive DataFrame copies,
metadata calculated from current data, updates, and clearing all datasets.
Stored data is lost when the process stops.

API endpoints and the sample dataset will be added in subsequent commits.

## Tests

```bash
python -m pytest -q
```

Storage tests in `tests/test_storage.py` cover ID assignment, copy isolation,
updated metadata, missing IDs, clearing storage, and DEBUG logging.
