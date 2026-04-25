from dataclasses import dataclass
from uuid import UUID
from enum import Enum

class Role(Enum):
    SUPERADMIN = "superadmin"
    ADMIN = "admin"
    EXECUTOR = "executor"
    REQUESTER = "requester"

@dataclass
class CurrentUser:
    id: UUID
    role: Role
