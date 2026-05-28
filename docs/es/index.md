# Documentación de DNS Orchestration

Bienvenido a la documentación de DNS Orchestration.

DNS Orchestration es un sistema de automatización DNS multi-proveedor diseñado para mantener los registros DNS sincronizados con cambios en el estado del sistema, como actualizaciones de IP pública.

## Visión general del sistema

El sistema se compone de tres partes principales:

- **Backend FastAPI (Control Plane)**  
  Gestiona configuración, providers, registros y estado del sistema.

- **Worker (Motor de ejecución)**  
  Aplica cambios DNS ejecutando ciclos de sincronización basados en el estado.

- **Dashboard Frontend**  
  Proporciona visibilidad de registros, providers y estado actual del sistema.

## Propósito principal

El objetivo principal de DNS Orchestration es garantizar consistencia DNS entre múltiples proveedores sin intervención manual.

La sincronización es completamente automática y basada en cambios de estado, no en triggers manuales.

## Conceptos clave

- **Provider**: Integración con proveedor DNS externo con esquema definido.
- **Record**: Entrada lógica de DNS gestionada por el sistema.
- **State**: Estado global del sistema que dispara sincronización (ej. cambios de IP pública).
- **Sync Cycle**: Proceso del worker que evalúa y aplica cambios DNS.

## Principio de arquitectura

DNS Orchestration sigue una separación estricta de responsabilidades:

- La API define y expone estado
- El worker ejecuta cambios
- El frontend visualiza el estado

Ningún componente concentra todas las responsabilidades.

## Estructura de documentación

- Architecture → Diseño del sistema e interacción entre componentes
- Worker → Modelo de ejecución y lógica de sincronización
- Data Model → Entidades y esquemas principales
- Sync Flow → Comportamiento extremo a extremo del sistema