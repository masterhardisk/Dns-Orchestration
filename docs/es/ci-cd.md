# CI/CD

## Descripción

DNS Orchestration utiliza un pipeline CI/CD completamente automatizado basado en GitHub Actions.

El sistema sigue un modelo de **publicación continua**, donde cada commit en main puede generar una nueva versión estable del sistema.



## Modelo de releases

El versionado es automático mediante SemVer:

* Cada commit en main dispara un análisis de versión
* Se revisan los commits desde el último tag existente
* Se calcula una nueva versión automáticamente
* Se crea un tag Git (vX.Y.Z)
* Se construye y publica la imagen Docker
* Se actualiza el tag latest



## Estrategia de versionado

- `feat:` → incremento de minor
- `fix:` → incremento de patch
- `BREAKING CHANGE` → incremento de major

Ejemplo:

* v1.0.0 → feat → v1.1.0
* v1.1.0 → fix → v1.1.1
* v1.1.1 → breaking → v2.0.0

## Flujo de release (pipeline en main)

Cuando se ejecuta un push a main:

1. El workflow se ejecuta automáticamente
2. Se obtiene el último tag existente del repositorio
3. Si existe un tag previo:
    * Se toman los commits desde ese tag hasta HEAD
4. Si no existe ningún tag:
    * Se usa v0.0.0 como base interna del cálculo
    * Se analizan todos los commits del repositorio
5. Se calcula la nueva versión SemVer
6. Se crea el tag en el repositorio
7. Se construye la imagen Docker multi-arch
8. Se publica la imagen en GHCR
9. Se actualiza latest con la misma build

## Bootstrap (primer release)

Cuando no existen tags en el sistema:

* no hay referencia de versión previa
* se usa v0.0.0 como base
* se calcula la primera versión desde el historial completo
* se genera el primer tag automáticamente
* se publica la primera imagen Docker
* latest apunta a ese build

Este comportamiento ocurre únicamente una vez.

## Publicación Docker

Cada release genera:

- `vX.Y.Z`
- `latest` (siempre apunta al último estable)

## Estrategia de ramas

El repositorio se organiza en dos ramas principales:

### main → Producción

* Contiene el estado estable del sistema
* Cada commit puede generar un release automático
* Dispara pipeline CI/CD completo:
    * versionado SemVer
    * creación de tags
    * build de Docker image
    * publicación en GHCR
    * actualización de latest
* Representa el estado desplegable del sistema en producción

---

### develop → Desarrollo

* Rama de integración de nuevas funcionalidades
* No genera releases automáticos
* Puede contener cambios incompletos o experimentales
* Sirve como base para preparar releases hacia main

---

### Flujo de promoción

* feature branches → se integran en develop
* develop → se estabiliza
* develop → merge a main = release

## Notas importantes

* No es necesario crear tags manualmente
* El versionado es completamente automático
* El historial de commits determina la versión
* El sistema asume que main siempre es estado estable

## Convención de commits

* feat: nueva funcionalidad
* fix: corrección de bug
* BREAKING: cambio incompatible