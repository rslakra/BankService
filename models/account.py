from sqlalchemy import Boolean
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from core.base import Base
from core.enums.account_type import AccountType
from core.enums.transaction import TransactionType


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    account_number = Column(String, unique=True, index=True)
    account_type = Column(Enum(AccountType), nullable=False)
    balance = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    owner = relationship("User", back_populates="accounts")
    transactions = relationship("Transaction", back_populates="account")
    cards = relationship("Card", back_populates="account")
    outgoing_transfers = relationship("Transfer", foreign_keys="Transfer.from_account_id",
                                      back_populates="from_account")
    incoming_transfers = relationship("Transfer", foreign_keys="Transfer.to_account_id", back_populates="to_account")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.account_number:
            import random
            self.account_number = f"{random.randint(1000000000, 9999999999)}"


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(String)
    reference_number = Column(String, unique=True, index=True)
    timestamp = Column(DateTime, default=func.now())

    # Relationships
    account = relationship("Account", back_populates="transactions")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.reference_number:
            import uuid
            self.reference_number = str(uuid.uuid4())


class Transfer(Base):
    __tablename__ = "transfers"

    id = Column(Integer, primary_key=True, index=True)
    from_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    to_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(String)
    reference_number = Column(String, unique=True, index=True)
    timestamp = Column(DateTime, default=func.now())

    # Relationships
    from_account = relationship("Account", foreign_keys=[from_account_id], back_populates="outgoing_transfers")
    to_account = relationship("Account", foreign_keys=[to_account_id], back_populates="incoming_transfers")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.reference_number:
            import uuid
            self.reference_number = str(uuid.uuid4())
