from dataclasses import dataclass, field
from enum import Enum
from typing import Set


class TicketStatus(str, Enum):
    NEW = "NEW"
    IN_PROGRESS = "IN_PROGRESS"
    PAUSED = "PAUSED"
    DONE = "DONE"
    CANCELLED = "CANCELLED"
    CLOSED = "CLOSED"

@dataclass
class Ticket:
    id: str
    creator_id: str
    status: TicketStatus = TicketStatus.NEW
    participants: Set[str] = field(default_factory=set)
