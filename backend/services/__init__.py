# ===============================
# Composition Root (WTS)
# ===============================

# -------------------------------
# Repositories
# -------------------------------
from db.session_repo import SessionRepo
from db.ticket_repo import TicketRepo
from db.participant_repo import ParticipantRepo

session_repo = SessionRepo()
ticket_repo = TicketRepo()
participant_repo = ParticipantRepo()

# -------------------------------
# Audit Service (WTS stub)
# -------------------------------
class AuditService:
    async def log_event(
        self,
        event_type: str,
        user_id: str,
        ticket_id: str | None = None,
        payload: dict | None = None,
    ):
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
    participant_repo=participant_repo,  # ✅ ЕДИНСТВЕННОЕ НОВОЕ
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