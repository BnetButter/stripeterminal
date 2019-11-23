import enum

class errno(enum.Enum):
    """Possible errors thrown by the Stripe JS SDK"""
    
    no_established_connection = enum.auto()
    no_active_colect_payment_method_attempt = enum.auto()
    no_active_read_reusable_card_attempt = enum.auto()
    canceled = enum.auto()
    cancelable_already_canceled = enum.auto()
    network_error = enum.auto()
    network_timeout = enum.auto()
    already_connected = enum.auto()
    failed_fetch_connection_token = enum.auto()
    discovered_too_manu_readers = enum.auto()
    invalid_reader_version = enum.auto()
    reader_error = enum.auto()
    command_already_in_progress = enum.auto()
    Error = enum.auto()




class StripeError(Exception):
    """Raised when Error is thrown by JS client terminal object"""

    def __init__(self, error, message):
        super().__init__(message)
        self.errno = getattr(errno, error)