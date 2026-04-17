from domain.ticket import TicketStatus

ALLOWED_STATUS_TRANSITIONS: dict[TicketStatus, set[TicketStatus]] = {
    TicketStatus.NEW: {TicketStatus.ACTIVE, TicketStatus.CANCELLED},
    TicketStatus.ACTIVE: {TicketStatus.PAUSED, TicketStatus.DONE},
    TicketStatus.PAUSED: {TicketStatus.ACTIVE, TicketStatus.DONE, TicketStatus.CANCELLED},
    TicketStatus.DONE: set(),
    TicketStatus.CANCELLED: set(),
}
