"""Exercise the API through HTTP requests without starting a server."""

import pytest
from fastapi.testclient import TestClient

import main


@pytest.fixture
def client():
    main.storage.clear()
    with TestClient(main.app) as test_client:
        yield test_client
    main.storage.clear()


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "1.0.0"}


def test_upload_and_retrieve_preserve_order_missing_values_and_storage(client):
    contents = b"student_id,score\n1,80\n2,90\n2,90\n3,\n4,unknown\n5,85\n"
    response = client.post("/upload", files={"file": ("sample.CSV", contents, "text/csv")})
    assert response.status_code == 200
    assert response.json() == {
        "id": 1, "filename": "sample.CSV", "rows": 6, "columns": 2,
        "column_names": ["student_id", "score"],
    }
    limited = client.get("/datasets/1", params={"limit": 2})
    assert limited.status_code == 200
    assert limited.json() == {
        "id": 1,
        "data": [{"student_id": 1, "score": "80"}, {"student_id": 2, "score": "90"}],
        "total_rows": 6,
    }
    full = client.get("/datasets/1").json()
    assert len(full["data"]) == full["total_rows"] == 6
    assert full["data"][2] == full["data"][1]
    assert full["data"][3]["score"] is None


@pytest.mark.parametrize("filename,contents", [
    ("data.txt", b"a\n1\n"),
    ("data", b"a\n1\n"),
    ("empty.csv", b""),
    ("bad.csv", b'a,b\n"unterminated'),
    ("encoding.csv", b"a\n\xff\n"),
])
def test_invalid_uploads_return_400_without_saving(client, filename, contents):
    response = client.post("/upload", files={"file": (filename, contents)})
    assert response.status_code == 400
    assert response.json()["detail"]
    assert main.storage.get(1) is None


def test_missing_dataset_returns_404(client):
    assert client.get("/datasets/999").status_code == 404


@pytest.mark.parametrize("limit", [0, -1, "invalid"])
def test_invalid_limit_returns_422(client, limit):
    assert client.get("/datasets/1", params={"limit": limit}).status_code == 422


def test_default_limit_is_100(client):
    contents = "number\n" + "\n".join(str(i) for i in range(105))
    response = client.post("/upload", files={"file": ("numbers.csv", contents)})
    assert response.status_code == 200
    result = client.get("/datasets/1").json()
    assert len(result["data"]) == 100
    assert result["total_rows"] == 105
