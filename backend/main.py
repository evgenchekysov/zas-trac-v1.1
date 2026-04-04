# =========================
#  main.py  (ZAS-TRAC)
# =========================

import os
import asyncio
from contextlib import asynccontextmanager, contextmanager
from datetime import datetime, timezone, timedelta

from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, Body
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import text, inspect

import uvicorn
import httpx

# --- .env (необязателен — если установлен пакет) ---
try:
    from dotenv import load_dotenv  # pip install python-dotenv
    load_dotenv()
except Exception:
    pass

from passlib.context import CryptContext  # pip install passlib[bcrypt]

import models
from database import get_db, engine

from typing import Optional, List
from pydantic import BaseModel
from sqlalchemy import or_, func

# --- СХЕМЫ: оборудование ---
class AssetCreate(BaseModel):
    qr_code: str
    name: str
    location: Optional[str] = ""

class AssetUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None

class AssetOut(BaseModel):
    qr_code: str
    name: str
    location: Optional[str] = ""


# --- СХЕМЫ: пользователи ---
class UserCreate(BaseModel):
    login: str
    full_name: str
    password: str
    role: models.UserRole

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    password: Optional[str] = None   # если пусто/None — не менять
    role: Optional[models.UserRole] = None

class UserOut(BaseModel):
    id: int
    login: str
    full_name: str
    role: models.UserRole

# -----------------------------
# БЛОК A. ФЛАГИ И НАСТРОЙКИ
# -----------------------------
RUN_BACKGROUND: bool = os.getenv("RUN_BACKGROUND", "1") == "1"
DB_CREATE_ALL: bool = os.getenv("DB_CREATE_ALL", "0") == "1"

# Одноразовое создание схемы (включай DB_CREATE_ALL=1 только на первый запуск новой БД)
if DB_CREATE_ALL:
    try:
        models.Base.metadata.create_all(bind=engine)
        print("[INFO] DB schema created (create_all).")
    except Exception as e:
        print(f"[WARN] create_all failed: {e}")

origins = os.getenv("CORS_ORIGINS", "*").split(",")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

BOT_TOKEN = os.getenv("TG_BOT_TOKEN", "").strip()
SUPERADMIN_TG_ID = int(os.getenv("TG_SUPERADMIN_TG_ID", "0") or 0)


# -----------------------------
# БЛОК B. ВСПОМОГАТЕЛЬНЫЕ
# -----------------------------
def get_now() -> datetime:
    """UTC без tzinfo (совместимость с DateTime без TZ в БД)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def format_seconds(seconds: int) -> str:
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return f"{hours}ч {minutes}м"


def verify_password(plain: str, hashed: Optional[str]) -> bool:
    """Проверка пароля (bcrypt); DEV‑fallback — прямое сравнение, если хэш не установлен."""
    hashed = hashed or ""
    try:
        if hashed.startswith("$2"):
            return pwd_context.verify(plain, hashed)
        return plain == hashed
    except Exception:
        return False


@contextmanager
def db_session():
    """Безопасная выдача Session для фоновых задач."""
    db = next(get_db())
    try:
        yield db
    finally:
        try:
            db.close()
        except Exception:
            pass


async def send_tg_alert(message: str):
    """Асинхронная отправка уведомлений в Telegram (без падений, если не настроено)."""
    if not BOT_TOKEN or not SUPERADMIN_TG_ID:
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": SUPERADMIN_TG_ID, "text": message, "parse_mode": "HTML"}
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            await client.post(url, json=payload)
    except Exception as e:
        print(f"❌ TG Error: {e}")


# -----------------------------
# БЛОК C. ФОНОВЫЕ ЗАДАЧИ
# -----------------------------
async def remind_unassigned_tickets():
    """Каждые 5 минут напоминаем о NEW-заявках, висящих 5+ минут без назначения."""
    while True:
        try:
            await asyncio.sleep(300)
            limit = get_now() - timedelta(minutes=5)
            with db_session() as db:
                items = (
                    db.query(models.Ticket)
                    .filter(
                        models.Ticket.status == models.TicketStatus.new,
                        models.Ticket.created_at <= limit,
                    )
                    .all()
                )
                for t in items:
                    msg = (
                        f"<b>🔔 НАПОМИНАНИЕ (5 мин+)</b>\n"
                        f"Заявка №{t.id} не назначена!\n"
                        f"📍 {t.asset_qr}"
                    )
                    await send_tg_alert(msg)
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"[BG] remind_unassigned_tickets: {e}")


async def auto_pause_shift_end():
    """В 23:00 ставим активные работы на паузу, начисляя накопленное время."""
    while True:
        try:
            now_local = datetime.now()
            if now_local.hour == 23 and now_local.minute == 0:
                with db_session() as db:
                    active = (
                        db.query(models.Ticket)
                        .filter(models.Ticket.status == models.TicketStatus.in_progress)
                        .all()
                    )
                    now = get_now()
                    for t in active:
                        if t.last_status_change:
                            delta = (now - t.last_status_change).total_seconds()
                            t.total_work_time += int(delta)
                        t.status = models.TicketStatus.paused
                        t.last_status_change = now
                    db.commit()
                await send_tg_alert("🌙 <b>ZAS-TRAC:</b> Смена окончена. Активные задачи поставлены на паузу.")
                await asyncio.sleep(65)
            await asyncio.sleep(30)
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"[BG] auto_pause_shift_end: {e}")
            await asyncio.sleep(60)


@asynccontextmanager
async def lifespan(app: FastAPI):
    task_remind = task_pause = None
    if RUN_BACKGROUND:
        task_remind = asyncio.create_task(remind_unassigned_tickets())
        task_pause = asyncio.create_task(auto_pause_shift_end())
        print("🚀 ZAS-TRAC: планировщики активны.")
    try:
        yield
    finally:
        for t in (task_remind, task_pause):
            if t:
                t.cancel()
        print("🛑 ZAS-TRAC: планировщики остановлены.")


# -----------------------------
# БЛОК D. ПРИЛОЖЕНИЕ
# -----------------------------
app = FastAPI(title="ZAS-TRAC Pro", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if origins == ["*"] else origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Статика
app.mount("/static", StaticFiles(directory="static"), name="static")


# -----------------------------
# БЛОК E. СТРАНИЦЫ
# -----------------------------
@app.get("/")
async def page_login():
    return FileResponse("static/login.html")

@app.get("/user-home")
async def page_home():
    return FileResponse("static/user-home.html")

@app.get("/create-ticket")
async def page_create():
    return FileResponse("static/index.html")  # убедись в регистре файла

@app.get("/admin-panel")
async def page_admin():
    return FileResponse("static/admin.html")

@app.get("/my-tickets")
async def page_my():
    return FileResponse("static/my-tickets.html")


# -----------------------------
# БЛОК F. HEALTH / DIAG (кросс‑СУБД)
# -----------------------------
@app.get("/healthz")
def health():
    return {"ok": True}

@app.get("/diag/db")
def diag_db():
    dialect = engine.dialect.name  # 'sqlite' / 'postgresql' ...
    try:
        with engine.connect() as conn:
            if dialect == "sqlite":
                row = conn.execute(text("select sqlite_version()")).fetchone()
                return {"dialect": dialect, "version": row[0], "database": "zastrac.db"}
            else:
                row = conn.execute(text("select version()")).fetchone()
                dbname = None
                try:
                    dbname = conn.execute(text("select current_database()")).fetchone()[0]
                except Exception:
                    pass
                return {"dialect": dialect, "version": str(row[0]), "database": dbname}
    except Exception as e:
        return {"dialect": dialect, "error": str(e)}

@app.get("/diag/tables")
def diag_tables():
    try:
        return inspect(engine).get_table_names()
    except Exception as e:
        return {"error": str(e)}


# -----------------------------
# БЛОК G. АВТОРИЗАЦИЯ (упрощённая)
# -----------------------------
@app.post("/auth/login")
def login(username: str, password: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.login == username).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Ошибка входа")
    role_value = user.role.value if hasattr(user.role, "value") else user.role
    return {"role": role_value, "full_name": user.full_name, "status": "success"}


# -----------------------------
# БЛОК H. ЗАЯВКИ И РАБОЧЕЕ ВРЕМЯ
# -----------------------------
@app.post("/tickets/create")
async def create_ticket(
    qr_code: str,
    description: str,
    background_tasks: BackgroundTasks,  # можно не использовать, оставлен для совместимости
    db: Session = Depends(get_db),
):
    clean_qr = qr_code.strip().upper()
    asset = db.query(models.Asset).filter(models.Asset.qr_code == clean_qr).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Объект не найден")

    now = get_now()
    t = models.Ticket(
        asset_qr=clean_qr,
        description=description,
        status=models.TicketStatus.new,
        created_at=now,
        last_status_change=now,
    )
    db.add(t)
    db.commit()
    db.refresh(t)

    msg = (
        f"<b>🆕 НОВАЯ ЗАЯВКА №{t.id}</b>\n"
        f"📍 Объект: {asset.name} ({clean_qr})\n"
        f"📝: {description}"
    )
    # Рассылаем в фоне (без блокировки запроса)
    asyncio.create_task(send_tg_alert(msg))
    return {"status": "success", "id": t.id}


@app.post("/tickets/{ticket_id}/status")
async def update_status(
    ticket_id: int,
    status: models.TicketStatus,
    background_tasks: BackgroundTasks,  # опционально
    db: Session = Depends(get_db),
):
    ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404)

    now = get_now()

    # Старт новой сессии при переходе в работу
    if status == models.TicketStatus.in_progress:
        db.add(models.WorkSession(ticket_id=ticket.id, start_time=now))

    # Закрыть активную сессию при паузе/закрытии и суммировать время
    elif status in (models.TicketStatus.paused, models.TicketStatus.closed):
        active = (
            db.query(models.WorkSession)
            .filter(models.WorkSession.ticket_id == ticket_id,
                    models.WorkSession.end_time.is_(None))
            .first()
        )
        if active:
            active.end_time = now
            delta = (now - active.start_time).total_seconds()
            ticket.total_work_time += int(delta)

    ticket.status = status
    ticket.last_status_change = now
    db.commit()
    db.refresh(ticket)

    time_info = (
        f"\n⏱ Чистое время: {format_seconds(ticket.total_work_time)}"
        if status == models.TicketStatus.closed else ""
    )
    msg = f"<b>СТАТУС: {status.value.upper()}</b>\n🆔 №{ticket_id}\n📍 {ticket.asset_qr}{time_info}"
    asyncio.create_task(send_tg_alert(msg))
    return {"status": "success", "work_time": ticket.total_work_time}


@app.get("/scan/{qr_code}")
async def check_asset(qr_code: str, db: Session = Depends(get_db)):
    clean_qr = qr_code.strip().upper()
    asset = db.query(models.Asset).filter(models.Asset.qr_code == clean_qr).first()
    if not asset:
        raise HTTPException(status_code=404, detail=f"Код '{clean_qr}' не найден в реестре")
    return {"status": "success", "asset_name": asset.name, "location": asset.location, "qr_code": asset.qr_code}


@app.get("/admin/all-tickets")
def get_all_tickets(
    month: Optional[int] = None,
    year: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Список заявок за месяц (фильтр диапазоном по created_at — кросс‑СУБД)."""
    now = get_now()
    m = month or now.month
    y = year or now.year

    # Дата начала и конца интервала
    start = datetime(y, m, 1)
    if m == 12:
        end = datetime(y + 1, 1, 1)
    else:
        end = datetime(y, m + 1, 1)

    tickets = (
        db.query(models.Ticket)
        .options(
            joinedload(models.Ticket.asset),
            selectinload(models.Ticket.assigned_workers),
            selectinload(models.Ticket.sessions),
        )
        .filter(models.Ticket.created_at >= start,
                models.Ticket.created_at < end)
        .all()
    )

    order = {
        models.TicketStatus.new: 0,
        models.TicketStatus.in_progress: 1,
        models.TicketStatus.paused: 2,
        models.TicketStatus.closed: 3,
    }
    tickets_sorted = sorted(tickets, key=lambda t: order.get(t.status, 99))

    return [
        {
            "id": t.id,
            "asset_name": t.asset.name if t.asset else "Объект",
            "qr_code": t.asset_qr,
            "description": t.description,
            "status": t.status.value if hasattr(t.status, "value") else str(t.status),
            "created_at": (t.created_at.isoformat() + "Z") if t.created_at else None,
            "total_work_time": t.total_work_time,
            "worker_names": [w.full_name for w in t.assigned_workers],
            "sessions": [
                {
                    "start_time": s.start_time.isoformat() + "Z",
                    "end_time": s.end_time.isoformat() + "Z" if s.end_time else None,
                }
                for s in t.sessions
            ],
        }
        for t in tickets_sorted
    ]


@app.post("/tickets/{ticket_id}/assign")
async def assign_workers(
    ticket_id: int,
    worker_ids: List[int] = Body(...),
    db: Session = Depends(get_db),
):
    ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404)

    workers = db.query(models.User).filter(models.User.id.in_(worker_ids)).all()
    now = get_now()

    ticket.assigned_workers = workers
    ticket.status = models.TicketStatus.in_progress
    ticket.last_status_change = now

    db.add(models.WorkSession(ticket_id=ticket.id, start_time=now))
    db.commit()
    return {"status": "success"}


@app.get("/admin/workers")
def get_workers(db: Session = Depends(get_db)):
    workers = db.query(models.User).filter(models.User.role == models.UserRole.worker).all()
    return [
        {
            "id": w.id,
            "full_name": w.full_name,
            "active_tasks": len([t for t in w.assigned_tickets
                                 if t.status != models.TicketStatus.closed]),
        }
        for w in workers
    ]

# -----------------------------
# БЛОК: создание оборудования из браузера
# -----------------------------
from pydantic import BaseModel

class AssetCreate(BaseModel):
    qr_code: str
    name: str
    location: str | None = ""

@app.post("/admin/assets")
def create_asset(data: AssetCreate, db: Session = Depends(get_db)):
    qr = data.qr_code.strip().upper()
    exists = db.query(models.Asset).filter(models.Asset.qr_code == qr).first()
    if exists:
        raise HTTPException(status_code=400, detail="Такой QR уже есть")

    asset = models.Asset(
        qr_code=qr,
        name=data.name.strip(),
        location=(data.location or "").strip()
    )
    db.add(asset)
    db.commit()
    return {"ok": True, "qr_code": qr}

@app.get("/add-asset")
def page_add_asset():
    return FileResponse("static/add-asset.html")

# -----------------------------
# РЕЕСТР ОБОРУДОВАНИЯ (assets)
# -----------------------------

@app.get("/admin/assets", response_model=dict)
def assets_list(
    q: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    query = db.query(models.Asset)
    if q:
        qnorm = f"%{q.strip().lower()}%"
        query = query.filter(
            or_(
                func.lower(models.Asset.qr_code).like(qnorm),
                func.lower(models.Asset.name).like(qnorm),
                func.lower(models.Asset.location).like(qnorm),
            )
        )
    total = query.count()
    rows = query.order_by(models.Asset.qr_code.asc()).limit(limit).offset(offset).all()
    items = [{"qr_code": a.qr_code, "name": a.name, "location": a.location} for a in rows]
    return {"total": total, "items": items}

@app.post("/admin/assets", response_model=AssetOut)
def assets_create(data: AssetCreate, db: Session = Depends(get_db)):
    qr = data.qr_code.strip().upper()
    if db.query(models.Asset).filter(models.Asset.qr_code == qr).first():
        raise HTTPException(status_code=400, detail="Такой QR уже существует")
    asset = models.Asset(qr_code=qr, name=data.name.strip(), location=(data.location or "").strip())
    db.add(asset); db.commit(); db.refresh(asset)
    return asset

@app.put("/admin/assets/{qr_code}", response_model=AssetOut)
def assets_update(qr_code: str, data: AssetUpdate, db: Session = Depends(get_db)):
    qr = qr_code.strip().upper()
    a = db.query(models.Asset).filter(models.Asset.qr_code == qr).first()
    if not a:
        raise HTTPException(status_code=404, detail="Объект не найден")
    if data.name is not None:
        a.name = data.name.strip()
    if data.location is not None:
        a.location = (data.location or "").strip()
    db.add(a); db.commit(); db.refresh(a)
    return a

@app.delete("/admin/assets/{qr_code}", response_model=dict)
def assets_delete(qr_code: str, db: Session = Depends(get_db)):
    qr = qr_code.strip().upper()
    a = db.query(models.Asset).filter(models.Asset.qr_code == qr).first()
    if not a:
        raise HTTPException(status_code=404, detail="Объект не найден")
    db.delete(a); db.commit()
    return {"ok": True}

# -----------------------------
# РЕЕСТР ПОЛЬЗОВАТЕЛЕЙ (users)
# -----------------------------

@app.get("/admin/users", response_model=dict)
def users_list(
    q: Optional[str] = None,
    role: Optional[models.UserRole] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    query = db.query(models.User)
    if q:
        qnorm = f"%{q.strip().lower()}%"
        query = query.filter(
            or_(
                func.lower(models.User.login).like(qnorm),
                func.lower(models.User.full_name).like(qnorm),
            )
        )
    if role:
        query = query.filter(models.User.role == role)
    total = query.count()
    rows = query.order_by(models.User.id.asc()).limit(limit).offset(offset).all()
    items = [{"id": u.id, "login": u.login, "full_name": u.full_name, "role": u.role} for u in rows]
    return {"total": total, "items": items}

@app.post("/admin/users", response_model=UserOut)
def users_create(data: UserCreate, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.login == data.login).first():
        raise HTTPException(status_code=400, detail="Логин уже существует")
    # хэшируем если есть bcrypt, иначе оставим plaintext (DEV)
    try:
        hashed = pwd_context.hash(data.password)
    except Exception:
        hashed = data.password
    u = models.User(
        login=data.login.strip(),
        full_name=data.full_name.strip(),
        password_hash=hashed,
        role=data.role,
    )
    db.add(u); db.commit(); db.refresh(u)
    return u

@app.put("/admin/users/{user_id}", response_model=UserOut)
def users_update(user_id: int, data: UserUpdate, db: Session = Depends(get_db)):
    u = db.query(models.User).filter(models.User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    if data.full_name is not None:
        u.full_name = data.full_name.strip()
    if data.role is not None:
        u.role = data.role
    if data.password:
        try:
            u.password_hash = pwd_context.hash(data.password)
        except Exception:
            u.password_hash = data.password
    db.add(u); db.commit(); db.refresh(u)
    return u

@app.delete("/admin/users/{user_id}", response_model=dict)
def users_delete(user_id: int, db: Session = Depends(get_db)):
    u = db.query(models.User).filter(models.User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    db.delete(u); db.commit()
    return {"ok": True}

@app.get("/registry/assets")
def page_registry_assets():
    return FileResponse("static/assets-registry.html")

@app.get("/registry/users")
def page_registry_users():
    return FileResponse("static/users-registry.html")

# -----------------------------
# БЛОК I. ТОЧКА ВХОДА
# -----------------------------
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
