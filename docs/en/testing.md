# Testing Guide

This project supports running tests both locally and in Docker. The test environment is isolated using a dedicated Dockerfile stage (`test`).

---

## Testing Architecture

The project is clearly separated into the following stages:

| Stage   | Purpose |
|---------|-----------|
| runtime | application execution |
| test    | test execution with dev dependencies |


## Test Structure

Tests are located in:

`backend/tests/`

Example:

`backend/tests/test_check_ip_sync.py`

---

## 💻 Run tests locally (fast)

Useful for daily development.

1. Install dependencies

	```bash
	pip install -r backend/requirements.txt
	pip install -r backend/requirements-dev.txt
	```

2. Run tests

	```bash
	pytest backend/tests
	```

---

## 🐳 Run tests with Docker (isolated environment)

This is the official reproducible test environment.

1. Build test stage

	```bash
	docker build --target test -t dns-orchestration-test .
	```

2. Run tests

	```bash
	docker run --rm dns-orchestration-test
	```

- mismo entorno que CI
- incluye dependencias dev
- no depende de tu máquina


## 🧪 Debug tests on runtime (special cases only)

If you need to inspect the real application state:

```bash
docker run --rm -it dns-orchestration-dns-orchestration pytest backend/tests
```

⚠️ This mode is NOT reliable:

* does not guarantee dev dependencies
* does not reflect CI environment
* intended only for quick debugging

---
## 🧩 Docker Compose (IMPORTANT)

docker-compose.yml is intended exclusively for runtime execution.

```yaml
services:
  dns-orchestration:
    build:
      context: .
      target: runtime
```
👉 Compose does NOT run tests by design.

---

## 🚀 CI/CD (GitHub Actions)

The CI pipeline uses:

```bash
docker build --target test .
```
and runs:

```bash
pytest
```
---

## 🧠 Mental Model of the Project

* Compose → runtime (local service execution)
* Runtime Docker image → production execution
* Test Docker image → isolated validation
* CI → build + test using the test stage

