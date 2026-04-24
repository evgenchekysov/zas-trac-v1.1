# ===============================
# Composition Root (WTS)
# ===============================

# -------------------------------
# Repositories
# -------------------------------
from db.session_repo import SessionRepo
from db.ticket_repo import TicketRepo

session_repo = SessionRepo()
ticket_repo = TicketRepo()

# -------------------------------
# Audit Service (WTS stub)
# -------------------------------
from services.audit_service import log_event

class AuditService:
    async def log_event(
        self,
        event_type: str,
        user_id: str,
        ticket_id: str | None = None,
        payload: dict | None = None,
    ):
        # WTS: audit не влияет на рабочий процесс
        return None

audit_service = AuditService()

# -------------------------------
# Services
# -------------------------------
from services.session_service import SessionService
from services.ticket_service import TicketService

session_service = SessionService(
    session_repo=session_repo,
    ticket_repo=ticket_repo,
    audit_service=audit_service,
)

ticket_service = TicketService(
    ticket_repo=ticket_repo,
    session_repo=session_repo,
    audit_service=audit_service,
    session_service=session_service,
)

# -------------------------------
# Workflows
# -------------------------------
from services.session_workflow import Session_Workflow
from services.ticket_workflow import Ticket_Workflow

session_workflow = Session_Workflow(
    session_service=session_service,
    ticket_service=ticket_service,
)

ticket_workflow = Ticket_Workflow(
    ticket_service=ticket_service,
)
