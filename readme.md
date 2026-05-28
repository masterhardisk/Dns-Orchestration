<p align="center">
  <img src="docs/assets/logo.png" width="140" />
</p>

<h1 align="center">DNS Orchestration</h1>

<p align="center">
  Multi-provider DNS automation system with dynamic provider discovery and schema-driven UI
</p>

---

## 🚀 Overview

DNS Orchestration is an open source multi-provider DNS automation system designed to keep DNS records synchronized with dynamic system state changes, such as public IP updates.

The system is fully extensible: new DNS providers can be added without modifying the core logic.

Currently supported DNS providers include:

- Cloudflare ([REST API](https://developers.cloudflare.com/api/))

- STRATO DNS ([DynDNS](https://www.strato.es/faq/hosting/como-configurar-dyndns-para-tus-dominios/))

---
## 🧠 Key Features

- Multi-provider DNS support
- Automatic provider discovery (no manual registration)
- Frontend Dashboard (Schema-driven UI Layer) 
  Provides system visibility and configuration via dynamic forms generated from provider schemas.
- Worker-based synchronization engine
- REST API control plane
- Fully decoupled architecture (API / Worker / Frontend)
- Runtime provider registry

---

## 🖥 User Interface

The system includes a schema-driven web dashboard that dynamically renders forms and views based on provider definitions.

The UI is fully responsive and supports both desktop and mobile usage.

### 📱 Mobile & Desktop Preview

![UI Preview](docs/assets/ui-preview.png)

## 🏗 Architecture

The system is composed of three main components:

- **FastAPI Backend (Control Plane)**  
  Manages providers, records, and system state.

- **Worker (Execution Engine)**  
  Executes synchronization cycles and applies DNS updates.

- **Frontend Dashboard**  
  Provides visibility into providers, records, and system state.

## 🔄 Core Concept

The system is driven by state changes (not manual actions):

1. Detect system state change (e.g. public IP update)
2. Resolve affected DNS records
3. Load provider from registry
4. Execute update
5. Persist result

## 📦 Installation

See full installation guide:

- 🇬🇧 English: [Installation](docs/en/installation.md)
- 🇪🇸 Español: [Instalación](docs/es/installation.md)

## 📖 Documentation

Full documentation is available in both languages:

### 🇬🇧 English

- [Index](docs/en/index.md)
- [Installation](docs/en/installation.md)
- [Contributing](docs/en/contributing.md)
- [CI/CD](docs/en/ci-cd.md)
- [Testing](docs/en/testing.md)

### 🇪🇸 Español

- [Índice](docs/es/index.md)
- [Instalación](docs/es/installation.md)
- [Contribución](docs/es/contributing.md)
- [CI/CD](docs/es/ci-cd.md)
- [Testing](docs/es/testing.md)

## 🔌 Providers System

DNS providers are:

- Auto-discovered at runtime
- Registered via Python `__init_subclass__`
- Exposed via REST API
- No manual registration is required

### Provider contract

Each provider must implement:

- `update_record(record, ip)`
- `test_connection()`

Optional schemas:

- `get_provider_schema()`

- `get_record_schema()`

Optional translations:

- `get_i18n()` (required if `label_key` is used)

## 🔁 Provider Discovery Flow

1. Scan `backend.infrastructure.providers`

2. Import modules dynamically

3. Each provider registers itself via `__init_subclass__`

4. Registry is exposed at `/api/providers/types`

5. UI renders forms dynamically from schemas

## 🌐 API

The backend exposes a full REST API for managing providers, records and system state.

Once the service is running:

- Backend: `http://localhost:8010`

- Swagger UI (OpenAPI docs): `http://localhost:8010/docs`

- ReDoc: `http://localhost:8010/redoc`

## 🐳 Deployment

Built for Docker Compose using a prebuilt image:

`ghcr.io/masterhardisk/dns-orchestration:latest`

## ⚙️ CI/CD

The CI/CD pipeline is defined in GitHub Actions and handles automated versioning, tagging, and Docker publishing.

All detailed behavior is documented in:

- 🇬🇧 [CI/CD](docs/en/ci-cd.md)
- 🇪🇸 [CI/CD](docs/es/ci-cd.md)

The pipeline is responsible for:

- automatic versioning from commit history
- creation of Git tags
- Docker image build (multi-arch)
- publishing to GHCR
- updating `latest`

## 🧪 Testing

The project includes a dedicated testing strategy based on an isolated Docker `test` stage.

Tests validate core domain logic and provider synchronization behavior.

For full testing instructions, setup details, and troubleshooting, see:

- 🇬🇧 [Testing Guide](docs/en/testing.md)
- 🇪🇸 [Guía de Testing](docs/es/testing.md)

## 📁 Repository Structure

```bash
backend/
frontend/
docs/
├── en/
├── es/
└── assets/
```

## 🤝 Contributing

See contribution guidelines:

- 🇬🇧 [Contributing](docs/en/contributing.md)
- 🇪🇸 [Contribución](docs/es/contributing.md)

## 📌 Design Principles

- No manual provider registration
- Schema-driven UI generation
- Strict separation of concerns
- Minimal required contracts
- Extensible by design

## 📄 License

This project is licensed under the MIT License.

See [LICENSE](LICENSE) for more details.

## 👤 Maintainer

This project was created and is maintained by [MasterHardisk](https://gerardcontador.com).

---

<p align="center">
  Built for automation, extensibility, and clean system design.
</p>

