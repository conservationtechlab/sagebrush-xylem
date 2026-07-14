# Loading sagebase_schema.sql file into PostGIS

This explains how to load the schema into the PostGIS docker container.

## What the dump contains

A schema-only dump contains database objects such as `CREATE TABLE`, `CREATE VIEW`, `CREATE INDEX`.

## Prerequisites

- PostgreSQL server installed and running. See docker/compose.yml
- `psql` available on the machine where the restore will run. 
    - On Ubuntu: 
```bash
sudo apt install postgresql postgresql-contrib -y
```

- A target database already created.
- A user account with permission to connect and create objects in target database.

## Restore command

Load the schema dump with `psql`, replace [INFO] with your values:

```bash
psql -h <HOSTNAME> -U <USER> -d <SAGEBASE> -f schema_only.sql
```

`psql -f` executes the SQL commands in the file against the target database.

## Recommended workflow

1. Build docker container.
2. Run the restore with `psql -f`.
3. Check for errors, especially extension, role, or schema conflicts.
4. Verify the objects loaded correctly with `\dt` to show tables, `\dv` views, and `\dn` schemas
inside `psql`.
Example:

```bash
createdb -U postgres sagebase
psql -U postgres -d sagebase -f sagebase_schema.sql
psql -U postgres -d sagebase
```

Then inside `psql`:

```sql
\dn
\dt
\dv
```


Example \dt:

| Schema  | List of relations name   | Type  | Owner  |  
|---|---|---|---|  
| public  | annotation  | table  | sage_user  |  
| public  | class  | table  | sage_user  |  
| public  | ...  | table  | sage_user  |  
| public  | uom  | table  | sage_user  |  

## Common issues

### Database does not exist

`psql` will not create the database for a plain SQL schema file; 
create the target database using docker/compose.yml

## Useful variations

Restore while stopping on the first error:

```bash
psql -v ON_ERROR_STOP=1 -h localhost -U your_user -d your_db_name -f schema_only.sql
```

Preview the beginning of the dump before loading it:

```bash
head -n 40 schema_only.sql
```

Load a file and save a restore log:

```bash
psql -v ON_ERROR_STOP=1 -h localhost -U your_user -d your_db_name -f schema_only.sql 2>&1 | tee restore.log
```

