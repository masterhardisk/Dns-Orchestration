# CONTRIBUTING

## Introducción

DNS Orchestration es un sistema extensible basado en providers.

Los providers se integran mediante discovery automático de módulos Python y registro dinámico en tiempo de importación.

No es necesario registro manual.

## Objetivo del proyecto

El objetivo del proyecto es permitir añadir nuevos proveedores DNS simplemente creando un nuevo archivo Python, sin modificar el core del sistema.

## Arquitectura de providers

El sistema se basa en tres mecanismos principales:

* Discovery automático de módulos
* Registro dinámico mediante __init_subclass__
* Exposición vía API REST

## Sistema de discovery

Los providers se cargan automáticamente desde:

backend.infrastructure.providers

usando:

* pkgutil.iter_modules
* importlib.import_module

Se excluyen módulos internos:

* base
* factory
* discovery

Cada módulo importado puede registrar providers automáticamente.

## Registro automático

Los providers se registran en:

BaseDNSProvider.registry

El registro ocurre mediante:

init_subclass(type=…)

## Type del provider (OBLIGATORIO)

Cada provider debe definir:

type = "unique_name"

Este valor es obligatorio.

Si no se define:

* el provider NO se registra
* no aparece en /api/providers/types
* no es accesible desde UI ni backend

El type es el identificador principal del provider en todo el sistema.

## Endpoint de providers

Los providers registrados se exponen en:

/api/providers/types

Este endpoint devuelve todos los providers disponibles en runtime.

## Contrato base del provider (OBLIGATORIO)

Todos los providers deben heredar de:

BaseDNSProvider

Y deben implementar:

### update_record

update_record(self, record: dict, ip: str) -> ProviderResult

Responsable de actualizar el registro DNS en el proveedor externo.

Es el método principal del sistema para la actualización de IP pública.

### test_connection

test_connection(self) -> bool

Valida la configuración y conectividad con el proveedor.

Se utiliza desde la UI y backend.

### Provider Schema (OPCIONAL)

Los providers pueden definir:

get_provider_schema()

Define los campos de configuración del provider.

Ejemplo de uso:

* token
* password
* api key
* credenciales genéricas

### Record Schema (OPCIONAL)

Los providers pueden definir:

get_record_schema()

Define los campos necesarios para cada registro DNS.

Ejemplos:

* zone_id (Cloudflare)
* hostname
* ttl
* value

## Relación entre schemas e i18n

Si un provider define schemas con label_key, entonces:

👉 get_i18n() es obligatorio

## Regla

* Si NO hay label_key → i18n no es necesario
* Si HAY label_key → i18n es obligatorio

## Traducciones (i18n)

Los providers pueden definir:

get_i18n()

Este método provee las traducciones utilizadas por la UI para renderizar los schemas.

## Ejemplo

```python
{
    "key": "token",
    "type": "text",
    "label_key": "example.field_token",
    "required": True
}
```
requiere:

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

## Integración en la UI

La UI se genera dinámicamente a partir de:

* type del provider
* provider schema
* record schema
* i18n (si aplica)

No se requieren cambios manuales para soportar nuevos providers.

## Flujo del sistema

1. Se ejecuta load_providers()
2. Se escanean módulos en providers/
3. Se importan dinámicamente
4. Cada provider ejecuta __init_subclass__
5. Si tiene type, se registra en registry
6. El registry se expone vía API
7. La UI consume /api/providers/types
8. Se generan formularios dinámicos

## Contrato funcional

Cada provider debe implementar:

* update_record → actualiza DNS
* test_connection → valida conexión

## Flujo de actualización de IP

1. Detectar cambio de IP pública
2. Resolver provider desde registry
3. Instanciar provider
4. Ejecutar update_record(record, ip)
5. Persistir resultado

## Ejemplo mínimo

```python
from backend.infrastructure.providers.base import BaseDNSProvider
from backend.domain.providers.provider_result import ProviderResult


class ExampleProvider(BaseDNSProvider, type="example"):

    def test_connection(self) -> bool:
        return True

    def update_record(self, record: dict, ip: str) -> ProviderResult:
        return ProviderResult.UPDATED
```

## Buenas prácticas

* Mantener providers independientes del core
* No introducir lógica global fuera del provider
* Mantener update_record lo más simple posible
* test_connection no debe modificar estado
* schemas deben ser declarativos
* evitar lógica compleja en i18n

## Flujo de contribución

1. Crear archivo en providers/
2. Definir clase heredando BaseDNSProvider
3. Definir type obligatorio
4. Implementar update_record
5. Implementar test_connection
6. Añadir schemas si aplica
7. Añadir i18n si hay label_key
8. Verificar aparición en /api/providers/types
9. Probar UI
10. Abrir Pull Request

## Nota importante

El sistema está basado en:

* discovery automático
* registry dinámico
* contratos mínimos obligatorios
* UI completamente schema-driven

No existe registro manual de providers.