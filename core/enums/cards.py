from enum import Enum, unique, auto


@unique
class CardType(str, Enum):
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"


@unique
class CardStatus(str, Enum):
    ACTIVE = "ACTIVE"
    BLOCKED = "BLOCKED"
    EXPIRED = "EXPIRED"
