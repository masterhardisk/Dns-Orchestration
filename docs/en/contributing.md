# CONTRIBUTING

## Introduction

DNS Orchestration is an extensible system based on providers.

Providers are integrated through automatic Python module discovery and dynamic registration at import time.

No manual registration is required.

## Project objective

The goal of the project is to allow adding new DNS providers simply by creating a new Python file, without modifying the core system.

## Provider architecture

The system is based on three main mechanisms:

* Automatic module discovery
* Dynamic registration via __init_subclass__
* REST API exposure

## Discovery system

Providers are automatically loaded from:

backend.infrastructure.providers

using:

* pkgutil.iter_modules
* importlib.import_module

Internal modules are excluded:

* base
* factory
* discovery

Each imported module can automatically register providers.

## Automatic registration

Providers are registered in:

BaseDNSProvider.registry

Registration happens through:

init_subclass(type=…)

## Provider type (REQUIRED)

Each provider must define:

type = "unique_name"

This field is mandatory.

If not defined:

* the provider is NOT registered
* it does not appear in /api/providers/types
* it is not accessible from UI or backend

The type is the main identifier of the provider in the entire system.

## Providers endpoint

Registered providers are exposed at:

/api/providers/types

This endpoint returns all available providers at runtime.

## Base provider contract (REQUIRED)

All providers must inherit from:

BaseDNSProvider

And must implement:

### update_record

update_record(self, record: dict, ip: str) -> ProviderResult
	
Responsible for updating the DNS record in the external provider.
	
This is the main method used by the system for public IP updates.

### test_connection

test_connection(self) -> bool

Validates configuration and connectivity with the provider.

Used by both UI and backend.

### Provider Schema (OPTIONAL)

Providers may define:
	
get_provider_schema()
	
Defines the configuration fields for the provider.
	
Example use cases:
	
* token
* password
* API key
* generic credentials

### Record Schema (OPTIONAL)

Providers may define:
	
get_record_schema()
	
Defines the fields required for each DNS record.
	
Examples:
	
* zone_id (Cloudflare)
* hostname
* ttl
* value

## Relationship between schemas and i18n

If a provider defines schemas using label_key, then:

👉 get_i18n() is required

## Rule

* If there is NO label_key → i18n is not required
* If there IS label_key → i18n is required

## Translations (i18n)

Providers may define:

get_i18n()

This method provides translations used by the UI to render schema fields.

## Example

```python
{
    "key": "token",
    "type": "text",
    "label_key": "example.field_token",
    "required": True
}
```
requires:

```python
def get_i18n(self):
    return {
        "en": {
            "example.field_token": "Token"
        },
        "es": {
            "example.field_token": "Token"
        }
    }
```

## UI integration

The UI is dynamically generated from:

* provider type
* provider schema
* record schema
* i18n (if applicable)

No manual changes are required to support new providers.

## System flow

1. load_providers() is executed
2. Modules in providers/ are scanned
3. Modules are dynamically imported
4. Each provider executes __init_subclass__
5. If it has a type, it is registered in the registry
6. The registry is exposed via API
7. UI consumes /api/providers/types
8. Dynamic forms are generated

## Functional contract

Each provider must implement:

* update_record → updates DNS
* test_connection → validates connection

## IP update flow

1. Detect public IP change
2. Resolve provider from registry
3. Instantiate provider
4. Execute update_record(record, ip)
5. Persist result

## Minimal example

```python
from backend.infrastructure.providers.base import BaseDNSProvider
from backend.domain.providers.provider_result import ProviderResult


class ExampleProvider(BaseDNSProvider, type="example"):

    def test_connection(self) -> bool:
        return True

    def update_record(self, record: dict, ip: str) -> ProviderResult:
        return ProviderResult.UPDATED
```

## Best practices

* Keep providers independent from core
* Do not introduce global logic outside the provider
* Keep update_record as simple as possible
* test_connection must not modify state
* Schemas should be declarative
* Avoid complex logic in i18n

## Contribution flow

1. Create file in providers/
2. Define class inheriting BaseDNSProvider
3. Define required type
4. Implement update_record
5. Implement test_connection
6. Add schemas if needed
7. Add i18n if using label_key
8. Verify appearance in /api/providers/types
9. Test UI integration
10. Open Pull Request

## Important note

The system is based on:

* automatic discovery
* dynamic registry
* minimal required contracts
* fully schema-driven UI

There is no manual provider registration.