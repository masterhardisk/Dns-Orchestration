# Installation
## Quick deployment

The service is run using Docker Compose with a prebuilt image from GHCR.

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

## Execution
Start the service using Docker Compose:

```bash

docker compose up -d
```

## Access
The application will be available at:

```url
http://localhost:8010
```

## Update
To update to the latest version of the image:

```bash
docker compose pull
docker compose up -d
```

## Stop service
Stop the containers:

```bash
docker compose down
```

## Logs
View real-time logs:

```bash
docker compose logs -f
```

## Persistence
Data is stored in the volume:

```
/data
```

## Notes

* The internal container port is always 8010
* Only the host port can be changed (e.g. “9000:8010”)
* Initial configuration is defined via environment variables in Docker Compose. Certain options, such as Telegram configuration, can be modified dynamically from the web interface without requiring a redeploy