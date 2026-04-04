# =========================
#  models.py  (ZAS-TRAC)
# =========================

# --- БЛОК 1: ИМПОРТЫ ---
from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey, Text, BigInteger, Table, func,
    Enum as SAEnum, Index, CheckConstraint
)
from sqlalchemy.orm import relationship
from database import Base
import enum

# --- БЛОК 2: ENUM-ТИПЫ ---
class UserRole(str, enum.Enum):
    superadmin = "superadmin"
    admin = "admin"
    worker = "worker"
    user = "user"

class TicketStatus(str, enum.Enum):
    new = "new"
    in_progress = "in_progress"
    paused = "paused"
    closed = "closed"

# Если у тебя в Postgres уже СОЗДАНЫ нативные ENUM-типы и ты не хочешь трогать схему сейчас,
# поставь True. Если хочешь хранить строки (проще менять набор значений) — False.
NATIVE_ENUM = False  # <-- при необходимости поставь True

# --- БЛОК 3: M2M (Заявка ↔ Исполнитель) ---
ticket_workers = Table(
    "ticket_workers",
    Base.metadata,
    Column("ticket_id", Integer, ForeignKey("tickets.id", ondelete="CASCADE"), primary_key=True),
    Column("worker_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    extend_existing=True,
)

# --- БЛОК 4: WorkSession — периоды фактической работы ---
class WorkSession(Base):
    __tablename__ = "work_sessions"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False, index=True)

    start_time = Column(DateTime, nullable=False, server_default=func.now(), index=True)
    end_time   = Column(DateTime, nullable=True, index=True)

    ticket = relationship("Ticket", back_populates="sessions")

    __table_args__ = (
        Index("ix_work_sessions_ticket_start", "ticket_id", "start_time"),
    )

# --- БЛОК 5: User ---
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    login = Column(String(128), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(SAEnum(UserRole, native_enum=NATIVE_ENUM, length=32),
                  nullable=False, server_default=UserRole.user.value)
    tg_id = Column(BigInteger, nullable=True)

# --- БЛОК 6: Asset ---
class Asset(Base):
    __tablename__ = "assets"

    qr_code = Column(String(64), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    location = Column(Text)

# --- БЛОК 7: Ticket ---
class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    asset_qr = Column(String(64), ForeignKey("assets.qr_code"), nullable=False, index=True)
    description = Column(Text)

    status = Column(SAEnum(TicketStatus, native_enum=NATIVE_ENUM, length=32),
                    nullable=False, server_default=TicketStatus.new.value, index=True)

    created_at = Column(DateTime, nullable=False, server_default=func.now(), index=True)
    last_status_change = Column(DateTime, nullable=False, server_default=func.now(), index=True)
    total_work_time = Column(Integer, nullable=False, server_default="0")

    assigned_workers = relationship(
        "User", secondary=ticket_workers, backref="assigned_tickets", lazy="selectin"
    )
    asset = relationship("Asset", backref="tickets")
    sessions = relationship(
        "WorkSession", back_populates="ticket", cascade="all, delete-orphan", lazy="selectin"
    )

    __table_args__ = (
        CheckConstraint("total_work_time >= 0", name="ck_tickets_nonneg_worktime"),
        Index("ix_tickets_asset_status_created", "asset_qr", "status", "created_at"),
    )
