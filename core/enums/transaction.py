from enum import Enum, unique, auto


@unique
class TransactionType(str, Enum):
    CREDIT = "CREDIT"
    DEBIT = "DEBIT"
