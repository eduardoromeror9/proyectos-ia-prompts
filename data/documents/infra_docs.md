# Documentación de Infraestructura

## Base de Datos

La base de datos PostgreSQL corre en el puerto 5432. Las credenciales están en Vault bajo el path `secret/prod/postgres`. Nunca uses las credenciales de prod en local.

## Restaurar Backups

Para restaurar un backup de la base de datos: `pg_restore -U postgres -d mydb backup.dump`. Los backups se generan automáticamente cada noche a las 2am UTC.