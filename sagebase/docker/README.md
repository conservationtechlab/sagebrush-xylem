## PostGIS Docker Compose Setup
Runs PostGIS:18-3.6 container with Docker Compose.

### Files needed
Create a secrets/ directory next to docker-compose.yml with these files:

pg_user.txt

pg_password.txt

pg_db.txt

pg-entrypoint.sh

Contents:

pg_user.txt → database username

pg_password.txt → database password

pg_db.txt → database name

### Security Best Practice
Use the compose as documented with hardened external secrets and entrypoint script below. 
For testing purposes, the credentials can be hardcoded into the compose. To do so comment out the 
lines between
```bash
# SECURE -->
...
# <--
```
and uncomment the lines between
```bash
# INSECURE -->
...
#
```

#### Entrypoint script
The postgis image expects POSTGRES_USER, POSTGRES_PASSWORD, and POSTGRES_DB.
Wrapper script reads the mounted secret files and exports variables before starting PostgreSQL.

Use this script for secrets/pg-entrypoint.sh:

```bash
#!/usr/bin/env bash
set -e

file_env() {
  local var="$1"
  local fileVar="${var}_FILE"
  if [ -n "${!fileVar:-}" ] && [ -f "${!fileVar}" ]; then
    export "$var"="$(< "${!fileVar}")"
    unset "$fileVar"
  fi
}

file_env POSTGRES_USER
file_env POSTGRES_PASSWORD
file_env POSTGRES_DB

exec /usr/local/bin/docker-entrypoint.sh postgres
```

Then make it executable and ensure not world-readable:

```bash
chmod 700 -R secrets
chmod 600 secrets/*.txt
```

### Start the container
From the directory containing docker-compose.yml, start the service with:

```bash
docker compose up -d
```

To confirm it started correctly:

```bash
docker compose ps
docker compose logs -f postgres
```

Stop the stack with:

```bash
docker compose down
```

Restart just the database container with:

```bash
docker compose restart postgres
```

### Note
The POSTGRES_* settings are mainly used when PostgreSQL initializes a new data directory for the 
first time; if the mapped data directory already contains an existing cluster, 
changing the secret files later will not recreate the database or reset credentials automatically.
