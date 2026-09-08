from dataclasses import dataclass, field
from enum import Enum
from typing import Set


class TicketStatus(str, Enum):
    NEW = "NEW"
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    PAUSED = "PAUSED"
    DONE = "DONE"
    CANCELLED = "CANCELLED"   # legacy, убрать после ADR‑013
    CLOSED = "CLOSED"


class TicketPriority(str, Enum):
    EMERGENCY = "EMERGENCY"
    NORMAL = "NORMAL"
    PLANNED = "PLANNED"


class PriorityState(str, Enum):
    OPEN = "OPEN"
    LOCKED = "LOCKED"


@dataclass
class Ticket:
    id: str
    creator_id: str

    status: TicketStatus = TicketStatus.NEW

    priority: TicketPriority = TicketPriority.NORMAL
    priority_state: PriorityState = PriorityState.OPEN

    participants: Set[str] = field(default_factory=set)
