from pathlib import Path
import re
import sys
from textwrap import dedent
import argparse

# ======= argumentos =======
parser = argparse.ArgumentParser(
    description="Generación selectiva de componentes para tu aplicación."
)
parser.add_argument("-models", action="store_true", help="Generar solo los models.")
parser.add_argument("-schemas", action="store_true", help="Generar solo los schemas.")
parser.add_argument(
    "-repository", action="store_true", help="Generar solo el repository."
)
parser.add_argument("-service", action="store_true", help="Generar solo el servicio.")
parser.add_argument("-router", action="store_true", help="Generar solo el router.")
args = parser.parse_args()


# ======= función de fallo =======
def fail(msg: str) -> None:
    print(msg, file=sys.stderr)
    raise SystemExit(1)


# ======= input dominio =======
domain = input("Nombre del dominio: ").strip().lower()
if not re.fullmatch(r"[a-z][a-z0-9_]*", domain):
    fail("Nombre inválido. Usa minúsculas, números y _; debe empezar por letra.")

Pascal = "".join(p.capitalize() for p in domain.split("_"))

# ======= rutas =======
project_root = Path(".").resolve()
app_dir = project_root / "app"
domain_dir = app_dir / "domain" / domain
routers_dir = app_dir / "routers"
main_file = app_dir / "main.py"

if not main_file.exists():
    fail(
        f"No se encontró main.py en {main_file}. Ajusta el script si tu main está en app/main.py."
    )

# ======= crear carpetas/paquetes =======
domain_dir.mkdir(parents=True, exist_ok=True)
routers_dir.mkdir(parents=True, exist_ok=True)

for p in [app_dir, app_dir / "core", app_dir / "domain", domain_dir, routers_dir]:
    initf = p / "__init__.py"
    if not initf.exists():
        initf.write_text("", encoding="utf-8")

# ======= contenidos =======
models_py = dedent(
    f"""
from typing import Optional
from sqlmodel import SQLModel, Field

class {Pascal}(SQLModel, table=True):
    __tablename__ = "{domain}"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: Optional[str] = None
    status: Optional[str] = None
"""
)

schemas_py = dedent(
    f"""
from typing import Optional, List
from sqlmodel import SQLModel

class {Pascal}Base(SQLModel):
    name: Optional[str] = None
    email: Optional[str] = None
    status: Optional[str] = None

class {Pascal}Create({Pascal}Base):
    name: str

class {Pascal}Read({Pascal}Base):
    id: int
    name: str

class {Pascal}Update({Pascal}Base):
    pass

class {Pascal}Page(SQLModel):
    total: int
    items: List[{Pascal}Read]
"""
)

repository_py = dedent(
    f"""
from typing import Sequence, Optional, Any
from sqlmodel import Session, select
from sqlalchemy import func
from .models import {Pascal}

class {Pascal}Repository:
    def __init__(self, session: Session):
        self.session = session

    def list_with_filters(
        self, 
        offset: int = 0, 
        limit: int = 50,
        filters: dict[str, Any] | None = None
    ) -> Sequence[{Pascal}]:
        stmt = select({Pascal})
        if filters:
            for field, value in filters.items():
                if value is not None and hasattr({Pascal}, field):
                    col = getattr({Pascal}, field)
                    if isinstance(value, str):
                        stmt = stmt.where(col.ilike(f"%{{value}}%"))
                    else:
                        stmt = stmt.where(col == value)
        stmt = stmt.offset(offset).limit(limit)
        return self.session.exec(stmt).all()

    def count(self) -> int:
        stmt = select(func.count()).select_from({Pascal})
        return int(self.session.exec(stmt).one())

    def get(self, id: int) -> Optional[{Pascal}]:
        return self.session.get({Pascal}, id)

    def create(self, obj: {Pascal}) -> {Pascal}:
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def update(self, obj: {Pascal}, data: dict) -> {Pascal}:
        for key, value in data.items():
            setattr(obj, key, value)
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def delete(self, obj: {Pascal}) -> None:
        self.session.delete(obj)
        self.session.commit()
"""
)

service_py = dedent(
    f"""
from typing import List, Optional, Any
from sqlmodel import Session
from .models import {Pascal}
from .repository import {Pascal}Repository
from .schemas import {Pascal}Create, {Pascal}Update

class {Pascal}Service:
    def __init__(self, session: Session):
        self.repo = {Pascal}Repository(session)

    def list_with_total(
        self, offset: int, limit: int, filters: dict[str, Any] | None = None
    ) -> tuple[list[{Pascal}], int]:
        items_seq = self.repo.list_with_filters(offset=offset, limit=limit, filters=filters)
        items: List[{Pascal}] = list(items_seq)
        total = self.repo.count()
        return items, total

    def get(self, id: int) -> Optional[{Pascal}]:
        return self.repo.get(id)

    def create(self, data: {Pascal}Create) -> {Pascal}:
        obj = {Pascal}.model_validate(data.model_dump())
        return self.repo.create(obj)

    def update(self, id: int, data: {Pascal}Update) -> Optional[{Pascal}]:
        obj = self.repo.get(id)
        if not obj:
            return None
        return self.repo.update(obj, data.model_dump(exclude_unset=True))

    def delete(self, id: int) -> bool:
        obj = self.repo.get(id)
        if not obj:
            return False
        self.repo.delete(obj)
        return True
"""
)

router_py = dedent(
    f"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from app.core.db import get_session
from app.domain.{domain}.service import {Pascal}Service
from app.domain.{domain}.schemas import {Pascal}Create, {Pascal}Read, {Pascal}Page, {Pascal}Update

router = APIRouter(prefix="/{domain}", tags=["{domain}"])

def get_service(session: Session = Depends(get_session)) -> {Pascal}Service:
    return {Pascal}Service(session)

@router.get("", response_model={Pascal}Page)
def list_{domain}(
    offset: int = 0, 
    limit: int = 50,
    name: str | None = Query(None),
    email: str | None = Query(None),
    status: str | None = Query(None),
    svc: {Pascal}Service = Depends(get_service)
):
    filters = {{
        "name": name,
        "email": email,
        "status": status
    }}
    items, total = svc.list_with_total(offset=offset, limit=limit, filters=filters)
    return {Pascal}Page(total=total, items=items)

@router.get("/{id}", response_model={Pascal}Read)
def get_{domain}(id: int, svc: {Pascal}Service = Depends(get_service)):
    obj = svc.get(id)
    if not obj:
        raise HTTPException(status_code=404, detail="{Pascal} not found")
    return obj

@router.post("", response_model={Pascal}Read)
def create_{domain}(payload: {Pascal}Create, svc: {Pascal}Service = Depends(get_service)):
    return svc.create(payload)

@router.put("/{id}", response_model={Pascal}Read)
def update_{domain}(id: int, payload: {Pascal}Update, svc: {Pascal}Service = Depends(get_service)):
    obj = svc.update(id, payload)
    if not obj:
        raise HTTPException(status_code=404, detail="{Pascal} not found")
    return obj

@router.delete("/{id}")
def delete_{domain}(id: int, svc: {Pascal}Service = Depends(get_service)):
    ok = svc.delete(id)
    if not ok:
        raise HTTPException(status_code=404, detail="{Pascal} not found")
    return {{"ok": True}}
"""
)

# ======= escritura condicional =======
generate_all = not (
    args.models or args.schemas or args.repository or args.service or args.router
)

if generate_all or args.models:
    (domain_dir / "models.py").write_text(models_py, encoding="utf-8")
    print(f"✅ Models creados en: {domain_dir}")

if generate_all or args.schemas:
    (domain_dir / "schemas.py").write_text(schemas_py, encoding="utf-8")
    print(f"✅ Schemas creados en: {domain_dir}")

if generate_all or args.repository:
    (domain_dir / "repository.py").write_text(repository_py, encoding="utf-8")
    print(f"✅ Repository creado en: {domain_dir}")

if generate_all or args.service:
    (domain_dir / "service.py").write_text(service_py, encoding="utf-8")
    print(f"✅ Service creado en: {domain_dir}")

if generate_all or args.router:
    (routers_dir / f"{domain}.py").write_text(router_py, encoding="utf-8")
    print(f"✅ Router creado en: {routers_dir / (domain + '.py')}")

# ======= registrar en main.py solo si se genera el router =======
if generate_all or args.router:
    main_txt = main_file.read_text(encoding="utf-8")

    import_stmt = f"from app.routers.{domain} import router as {domain}_router"
    include_stmt = f"app.include_router({domain}_router)"

    if import_stmt not in main_txt:
        lines = main_txt.splitlines()
        last_import_idx = 0
        for i, l in enumerate(lines):
            if l.startswith("from ") or l.startswith("import "):
                last_import_idx = i
        lines.insert(last_import_idx + 1, import_stmt)
        main_txt = "\n".join(lines)

    if include_stmt not in main_txt:
        if "app = FastAPI" in main_txt and "include_router" in main_txt:
            lines = main_txt.splitlines()
            idxs = [i for i, l in enumerate(lines) if "include_router" in l]
            insert_at = idxs[-1] + 1 if idxs else len(lines)
            lines.insert(insert_at, include_stmt)
            main_txt = "\n".join(lines) + "\n"
        else:
            main_txt += "\n" + include_stmt + "\n"

    main_file.write_text(main_txt, encoding="utf-8")
    print("✅ Router registrado en main.py")
