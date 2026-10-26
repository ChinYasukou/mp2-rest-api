# MP2: Data Processing API

This DS3500 project provides a FastAPI REST API for uploading CSV datasets,
storing them temporarily in memory, validating and cleaning them with reusable
MP1 functions, and retrieving processed records. Processing returns separate
validation-removal counts and a cleaning report. Every response includes an
`X-Request-ID`; request logs record the method, path, status, and duration.

## Setup

From the repository root:

```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload
```

Open http://127.0.0.1:8000/docs for the interactive Swagger UI.

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
│   ├── utils.py
│   └── middleware.py
├── data_pipeline/
│   ├── __init__.py
│   ├── data_loaders.py
│   ├── data_processor.py
│   ├── data_validator.py
│   ├── data_output.py
│   └── utils.py
├── fixtures/
│   └── sample_data.csv
└── tests/
    ├── conftest.py
    ├── test_api.py
    ├── test_middleware.py
    └── test_storage.py
```

The `data_pipeline/` package contains copies of the reusable MP1 modules; a
separate MP1 checkout is not required. `src/` contains API-specific functionality.

## Endpoints

| Endpoint | Behavior |
| --- | --- |
| `GET /health` | Return `{"status": "ok", "version": "1.0.0"}`. |
| `POST /upload` | Upload a CSV using the multipart field `file`; return its ID, filename, row/column counts, and column names. |
| `GET /datasets/{dataset_id}?limit=2` | Return up to two records, the ID, and the full stored row count. Default limit: 100; minimum: 1. |
| `POST /datasets/{dataset_id}/process` | Validate and clean the stored dataset using the JSON settings below, then replace it and return a report. |

Successful requests return 200. Unsupported/unreadable CSV files, missing
configured columns, and unsupported enabled processing settings return 400.
Missing datasets return 404; invalid request types or parameters return 422.
Unexpected failures return a generic 500 response while the traceback is logged.

Storage assigns sequential IDs starting at 1, preserves filenames, and copies
DataFrames on save, read, and update. Metadata is calculated from current data.
Processing failures leave the stored dataset unchanged. All data is lost when
the server restarts; processing replaces data under the same ID.

## Upload → process → retrieve

In `/docs`, expand each endpoint and select **Try it out**, enter its inputs,
and select **Execute**:

1. Call `GET /health` and confirm status 200.
2. Upload `fixtures/sample_data.csv` using `POST /upload`. Expect six rows,
   two columns (`student_id`, `score`), and a positive integer ID.
3. Retrieve that ID with `limit=2`. Expect two rows and `total_rows: 6`.
   Before processing, scores are strings because the column contains `unknown`;
   missing scores are returned as `null`.
4. Process the uploaded ID with this JSON body:

```json
{
  "validation": {
    "required_columns": ["student_id", "score"],
    "numeric_columns": ["score"]
  },
  "processing": {
    "remove_duplicates": true,
    "missing": {"enabled": true, "axis": "rows"},
    "outliers": {
      "enabled": false,
      "columns": [],
      "method": "iqr",
      "threshold": 1.5
    }
  }
}
```

For dataset 1, expect:

```json
{
  "id": 1,
  "validation_rows_removed": 1,
  "cleaning_report": {
    "rows_before": 5,
    "rows_after": 3,
    "rows_removed": 2,
    "columns_before": 2,
    "columns_after": 2,
    "columns_removed": 0
  }
}
```

Validation removes the `unknown` score. Cleaning removes one duplicate and one
row with a missing score. Retrieve the same ID again: `total_rows` should be 3,
with student IDs 1, 2, 5 and numeric scores 80, 90, 85. Upload a fresh copy before
repeating a test that depends on the original six rows.

Settings may be omitted: validation lists default to empty, duplicate removal
and missing-row removal are enabled, and outlier removal is disabled. Missing
handling supports `rows` or `columns`; outlier methods are `iqr` and `zscore`.

To check errors, retrieve an unused ID (404), upload `README.md` (400), and
retrieve with `limit=0` (422). Inspect response headers for the eight-character
`X-Request-ID`. The terminal shows INFO request logs, WARNING logs for 4xx,
ERROR logs for 5xx, and DEBUG storage operations with verbose logging enabled.

## Automated tests

With the virtual environment activated:

```bash
python -m pytest tests -v
```

Tests cover the required sample upload, process/retrieve workflow, and missing
dataset response, plus CSV errors, row limits, atomic processing failures,
request IDs, log levels, generic 500 handling, and storage copy isolation.

The installed Starlette TestClient currently emits a deprecation warning for
its use of `httpx`. This warning does not prevent the tests from running.

## Completion

Parts 1 and 2 are implemented. Keep `venv/`, caches, generated logs, and `.env`
files out of Git. Commit and push changes before the assignment deadline.
