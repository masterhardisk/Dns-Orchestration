from enum import Enum

class ProviderResult(str, Enum):
    UPDATED = "updated"
    NO_CHANGE = "no_change"
    ERROR = "error"
    RATE_LIMIT = "rate_limit"