from domain.ticket import TicketStatus

ALLOWED_STATUS_TRANSITIONS: dict[TicketStatus, set[TicketStatus]] = {
    TicketStatus.NEW: {TicketStatus.IN_PROGRESS, TicketStatus.CANCELLED},
    TicketStatus.IN_PROGRESS: {TicketStatus.PAUSED, TicketStatus.DONE},
    TicketStatus.PAUSED: {TicketStatus.IN_PROGRESS, TicketStatus.DONE, TicketStatus.CANCELLED},
    TicketStatus.DONE: set(),
    TicketStatus.CANCELLED: set(),
}
