class TicketError(Exception):
    """Base domain error for tickets"""


class InvalidStatusTransition(TicketError):
    pass


class ParticipantError(TicketError):
    pass

class NotFound(Exception):
    def __init__(self, message: str = "Not found"):
        self.message = message
        super().__init__(message)


class Forbidden(Exception):
    def __init__(self, message: str = "Forbidden"):
        self.message = message
        super().__init__(message)
        