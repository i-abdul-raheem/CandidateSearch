# Candidate Search API

FastAPI service for uploading PDF resumes, searching candidates using multilingual
embeddings, and explaining job matches with a local Ollama model.

## Run locally

Requirements: Python 3.12+, `uv`, and Ollama with the configured model installed.

```bash
cp .env.example .env
uv sync --extra dev
uv run fastapi dev main.py
```

Environment variables are documented in `.env.example`. Relative `DATA_DIR` values
are resolved from the process working directory; the default data directory is always
the repository's `api/data` directory.

When `API_KEY` is set, send it in `X-API-Key` for `/`, `/apply`, and `/explain`.
Health endpoints remain unauthenticated for container orchestrators.

## Endpoints

- `GET /?q=python&top_k_people=3` searches indexed candidates.
- `POST /query` accepts full job descriptions as JSON without an application-level
  length limit. Long descriptions are embedded in chunks so later requirements are
  not silently truncated.
- `POST /apply` accepts one PDF as multipart field `file` and returns an opaque ID.
- `POST /explain` accepts `resume_id` and `jd_text` as JSON.
- `GET /file/{resume_id}` returns the uploaded PDF inline.
- `GET /talent` lists the indexed talent pool; `DELETE /talent/{resume_id}` removes a candidate.
- `/roles` provides recruiter role CRUD (`GET`, `POST`, `PUT`, `DELETE`).
- `GET /searches` lists persisted searches; `DELETE /searches/{id}` or `DELETE /searches` removes them.
- `GET /health/live` and `GET /health/ready` support operational probes.

Each search result uses the absolute resume URL as `id` and also contains the stable
`resume_id` used by `/explain`. When
API-key authentication is enabled, clients must also send `X-API-Key` when opening
the file URL.

API documentation is available at `/docs` except when `ENVIRONMENT=production`.

## Production notes

Mount `/app/data` on persistent storage, set `API_KEY`, restrict `CORS_ORIGINS`, and
run Ollama as a separately monitored service. Use one API worker: each worker loads a
large embedding model and Chroma's local persistence is not intended for horizontally
scaled writers. For multi-instance deployment, replace the local vector store with a
managed service and store uploaded documents in object storage.

Candidate resumes contain personal data. Define retention/deletion policies, encrypt
storage, restrict logs and backups, and complete the applicable privacy review before
processing real applicants.
