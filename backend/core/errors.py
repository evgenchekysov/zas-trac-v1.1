class TicketError(Exception):
    """Base domain error for tickets"""


class InvalidStatusTransition(TicketError):
    pass


class ParticipantError(TicketError):
    pass
