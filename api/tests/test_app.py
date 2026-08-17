from fastapi.testclient import TestClient

from src.app import create_app


def test_liveness() -> None:
    with TestClient(create_app()) as client:
        response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert response.headers["X-Content-Type-Options"] == "nosniff"


def test_public_api_is_in_openapi_schema() -> None:
    paths = create_app().openapi()["paths"]
    assert "/" in paths
    assert "/query" in paths
    assert "/apply" in paths
    assert "/explain" in paths
    assert "/file/{resume_id}" in paths
    assert "/talent" in paths
    assert "/roles" in paths
    assert "/searches" in paths


def test_file_endpoint_rejects_invalid_resume_id() -> None:
    with TestClient(create_app()) as client:
        response = client.get("/file/../../etc/passwd")
        encoded_response = client.get("/file/%2E%2E%2Fsecret")
    assert response.status_code == 404
    assert encoded_response.status_code == 404
