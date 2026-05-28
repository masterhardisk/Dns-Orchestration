# Testing Guide

Este proyecto soporta ejecución de tests tanto en local como en Docker. El entorno de tests está aislado mediante un stage específico del Dockerfile (`test`).

---

## Arquitectura de testing

El proyecto separa claramente:

| Stage   | Propósito |
|---------|-----------|
| runtime | ejecución de la app |
| test    | ejecución de tests con dependencias dev |


## Estructura de tests

Los tests se encuentran en:

`backend/tests/`

ejemplo:

`backend/tests/test_check_ip_sync.py`

---

## 💻 Ejecutar tests en local (rápido)

Útil para desarrollo diario.

1. Instalar dependencias

	```bash
	pip install -r backend/requirements.txt
	pip install -r backend/requirements-dev.txt
	```
2. Ejecutar tests

	```bash
	pytest backend/tests
	```

---

## 🐳 Ejecutar tests con Docker (entorno aislado)

Este es el entorno oficial de tests reproducible.

1. Build del stage de tests

	```bash
	docker build --target test -t dns-orchestration-test .
	```

2. Ejecutar tests

	```bash
	docker run --rm dns-orchestration-test
	```

- mismo entorno que CI
- incluye dependencias dev
- no depende de tu máquina


## 🧪 Debug de tests sobre runtime (solo casos puntuales)

Si necesitas inspeccionar el estado real de la app:

```bash
docker run --rm -it dns-orchestration-dns-orchestration pytest backend/tests
```

⚠️ Este modo NO es fiable:

* no garantiza dependencias dev
* no refleja entorno CI
* solo debugging rápido

---
## 🧩 Docker Compose (IMPORTANTE)

docker-compose.yml está pensado exclusivamente para runtime.

```yaml
services:
  dns-orchestration:
    build:
      context: .
      target: runtime
```
👉 Compose NO ejecuta tests por diseño.

---

## 🚀 CI/CD (GitHub Actions)

El pipeline de CI usa:

```bash
docker build --target test .
```
y ejecuta:

```bash
pytest
```
---

🧠 Regla mental del proyecto

* Compose → runtime (ejecución local del servicio)
* Dockerfile runtime → imagen de ejecución
* Dockerfile test → validación aislada
* CI → build + test en stage test

