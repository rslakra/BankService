from datetime import datetime
from typing import Optional

from pydantic import validator, field_serializer

from core.enums.account_type import AccountType
from core.enums.cards import CardType, CardStatus
from core.enums.transaction import TransactionType
from schemas.base import BaseSchema


# Account schemas
class AccountBase(BaseSchema):
    account_type: AccountType

    # @field_serializer("group")
    # def serialize_account_type(self, account_type: AccountType) -> str:
    #     """Serializes the Group enum to its name."""
    #     return account_type.name


class AccountCreate(AccountBase):
    initial_balance: Optional[float] = 0.0


class AccountResponse(AccountBase):
    id: int
    account_number: str
    balance: float
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Transaction schemas
class TransactionBase(BaseSchema):
    transaction_type: TransactionType
    amount: float
    description: Optional[str] = None

    @validator('amount')
    def validate_amount(cls, value):
        if value <= 0:
            raise ValueError('Amount must be positive')

        return value


class TransactionCreate(TransactionBase):
    pass


class TransactionResponse(TransactionBase):
    id: int
    account_id: int
    reference_number: str
    timestamp: datetime

    class Config:
        from_attributes = True


# Transfer schemas
class TransferBase(BaseSchema):
    from_account_id: int
    to_account_id: int
    amount: float
    description: Optional[str] = None

    @validator('amount')
    def validate_amount(cls, value):
        if value <= 0:
            raise ValueError('Amount must be positive')

        return value

    @validator('to_account_id')
    def validate_different_accounts(cls, value, values):
        if 'from_account_id' in values and value == values['from_account_id']:
            raise ValueError('Cannot transfer to the same account')

        return value


class TransferCreate(TransferBase):
    pass


class TransferResponse(TransferBase):
    id: int
    reference_number: str
    timestamp: datetime

    class Config:
        from_attributes = True


# Card schemas
class CardBase(BaseSchema):
    card_type: CardType
    credit_limit: Optional[float] = 0.0


class CardCreate(CardBase):
    pass


class CardResponse(CardBase):
    id: int
    account_id: int
    card_number: str
    status: CardStatus
    expiry_date: datetime
    created_at: datetime

    class Config:
        from_attributes = True


# Statement schemas
class StatementRequest(BaseSchema):
    start_date: Optional[str] = None
    end_date: Optional[str] = None
