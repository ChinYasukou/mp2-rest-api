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
│   └── sample_data.csv
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

Part 1 (API Foundation) is complete, including the three endpoints, sample CSV,
and automated tests. Part 2 (API Integration) is still to be implemented.

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

## Manual testing in Swagger UI

Start the server and open http://127.0.0.1:8000/docs. For each endpoint, select
**Try it out**, enter the inputs, and select **Execute**.

1. Call `GET /health`. Expect status 200 and
   `{"status": "ok", "version": "1.0.0"}`.
2. Call `POST /upload`, choosing `fixtures/sample_data.csv`. Expect status 200
   and metadata for six rows and two columns:

   ```json
   {
     "id": 1,
     "filename": "sample_data.csv",
     "rows": 6,
     "columns": 2,
     "column_names": ["student_id", "score"]
   }
   ```

   IDs increase with uploads, so use the actual returned ID below.
3. Call `GET /datasets/{dataset_id}` with that ID and `limit=2`. Expect status
   200 and the following response for ID 1:

   ```json
   {
     "id": 1,
     "data": [
       {"student_id": 1, "score": "80"},
       {"student_id": 2, "score": "90"}
     ],
     "total_rows": 6
   }
   ```

4. Retrieve the same dataset with `limit=100`. All six rows should remain,
   including the duplicate row. The missing score should be `null`; other
   scores are strings because the column contains `unknown`.
5. Request an unused ID such as `999`. Expect status 404.
6. Upload `README.md` to test an unsupported extension. Expect status 400.
7. Retrieve the uploaded dataset with `limit=0`. Expect status 422.

The terminal should show DEBUG storage operations, INFO upload/retrieval
messages, and WARNING messages for missing datasets and rejected uploads.
Uvicorn also prints its own server and access logs. Restarting the server
clears stored datasets and resets the ID counter.

## Tests

```bash
python -m pytest -q
```

Storage tests in `tests/test_storage.py` cover ID assignment, copy isolation,
updated metadata, missing IDs, clearing storage, and DEBUG logging.
API tests in `tests/test_api.py` cover the endpoints, upload errors, row limits,
row order, missing values, and retrieval without changing stored data.
