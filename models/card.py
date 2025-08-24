from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from core.base import Base
from core.enums.cards import CardType, CardStatus


class Card(Base):
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    card_number = Column(String, unique=True, index=True, nullable=False)
    card_type = Column(Enum(CardType), nullable=False)
    status = Column(Enum(CardStatus), default=CardStatus.ACTIVE)
    credit_limit = Column(Float, default=0.0)
    expiry_date = Column(DateTime)
    cvv = Column(String)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    account = relationship("Account", back_populates="cards")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.expiry_date:
            from datetime import datetime, timedelta
            self.expiry_date = datetime.utcnow() + timedelta(days=365 * 4)  # 4 years from now
        if not self.cvv:
            import random
            self.cvv = f"{random.randint(100, 999)}"
