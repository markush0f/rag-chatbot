# 🗂 Flujo de trabajo con Alembic (SQLAlchemy + PostgreSQL)

## 1️⃣ Inicializar el proyecto (solo la primera vez)

```bash
alembic init migrations
```

Esto crea:

```
alembic.ini
migrations/
  env.py
  script.py.mako
  versions/
```

---

## 2️⃣ Configuración básica

### En `alembic.ini`

```ini
[alembic]
script_location = migrations
# sqlalchemy.url = postgresql+psycopg2://user:pass@host/dbname

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stdout,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
```

---

### En `migrations/env.py`

* Importar tu `Base.metadata` (de tus modelos SQLAlchemy).
* Definir `target_metadata = Base.metadata`.
* Si no pones `sqlalchemy.url` en el `.ini`, asignarlo desde tu config de Python:

```python
from app.db import Base
from app.config import DB_URL

config.set_main_option("sqlalchemy.url", DB_URL)
target_metadata = Base.metadata
```

---

## 3️⃣ Editar tus modelos

* Añade/modifica tablas, columnas, claves foráneas, etc.
* Guarda cambios en tus modelos Python.

---

## 4️⃣ Autogenerar la revisión

```bash
alembic revision --autogenerate -m "descripcion_cambio"
# o
python -m alembic revision --autogenerate -m "descripcion_cambio"
```

Esto crea un archivo en `migrations/versions/`.

---

## 5️⃣ Revisar y corregir la migración

* **Revisar siempre el archivo generado** antes de aplicarlo.
* Cambiar `drop + create` por `op.rename_table` o `op.alter_column` si es un renombre.
* Añadir migraciones de datos si hace falta:

```python
op.execute("UPDATE tabla SET campo = 'valor' WHERE ...")
```

---

## 6️⃣ Aplicar la migración

```bash
alembic upgrade head          # aplica hasta la última revisión
alembic upgrade <revision_id> # aplica hasta revisión específica
```

---

## 7️⃣ Revertir migraciones

```bash
alembic downgrade -1           # deshace la última migración
alembic downgrade <revision_id> # vuelve a un punto concreto
```

---

## 8️⃣ Consultar estado e historial

```bash
alembic history   # ver todas las revisiones
alembic current   # ver en qué revisión está la DB
alembic heads     # ver ramas activas
```

---

## 9️⃣ Resolver ramas (merge)

Si hay múltiples `heads`:

```bash
alembic merge -m "merge heads" <head1> <head2>
```

Editar el merge y luego:

```bash
alembic upgrade head
```

---

## 🔟 Sincronizar DB existente sin aplicar migraciones

```bash
alembic stamp head
```

Esto marca la base como actual sin ejecutar cambios.

---

## 💡 Buenas prácticas

* **Siempre** revisar el archivo generado antes de `upgrade`.
* Usar convención de nombres para constraints/índices (`naming_convention` en `MetaData`).
* Ser explícito en cambios de esquema complejos (tipos, FKs).
* No meter lógica de aplicación dentro de migraciones.
* Usar `op.rename_table` / `op.alter_column` para conservar datos en renombres.

---

## 📌 Comandos más usados

```bash
# Crear migración
alembic revision --autogenerate -m "cambio"

# Aplicar migración
alembic upgrade head

# Revertir migración
alembic downgrade -1

# Estado
alembic history
alembic current
alembic heads

# Marcar DB como actual
alembic stamp head
```
