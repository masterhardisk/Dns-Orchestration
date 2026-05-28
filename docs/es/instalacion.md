# Instalación
## Despliegue rápido

El servicio se ejecuta mediante Docker Compose utilizando una imagen preconstruida desde GHCR.

```yaml
services:
  dns-orchestration:
    image: ghcr.io/masterhardisk/dns-orchestration:latest
    container_name: dns-orchestration
    ports:
      - "8010:8010"
    volumes:
      - dns_data:/data
    environment:
      TELEGRAM_ENABLED: "true"
      TELEGRAM_BOT_TOKEN: "xxxxx"
      TELEGRAM_CHAT_ID: "xxxxx"
    restart: unless-stopped
volumes:
  dns_data:
```

## Ejecución

Levanta el servicio con Docker Compose:

```bash

docker compose up -d
```

## Acceso

La aplicación estará disponible en:

```url
http://localhost:8010
```

## Actualización

Para actualizar a la última versión de la imagen:

```bash
docker compose pull
docker compose up -d
```

## Parar el servicio

Detener los contenedores:

```bash
docker compose down
```

## Logs

Ver logs en tiempo real:

```bash
docker compose logs -f
```

## Persistencia

Los datos se almacenan en el volumen:

```
/data
```

## Notas

* El puerto interno del contenedor es siempre 8010
* Solo se puede cambiar el puerto del host (ej: "9000:8010")
* La configuración inicial se define mediante variables de entorno en Docker Compose. Determinadas opciones, como la configuración de Telegram, pueden ser modificadas dinámicamente desde la interfaz de usuario sin necesidad de redeploy.