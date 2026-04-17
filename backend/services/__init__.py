from services.session_service import session_service
from services.ticket_service import ticket_service
from services.session_workflow import SessionWorkflow

session_workflow = SessionWorkflow(
    session_service=session_service,
    ticket_service=ticket_service,
)
