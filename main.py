from datetime import datetime
from typing import List, Optional

import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from config.base import get_settings
from core.database import init_database, get_database
from core.enums.transaction import TransactionType
from core.security import verify_token, verify_password, get_password_hash, create_access_token
from models.account import Account, Transaction, Transfer
from models.card import Card
from models.user import User
from schemas.account import AccountResponse, AccountCreate, TransactionCreate, TransactionResponse, TransferResponse, \
    TransferCreate, CardResponse, CardCreate
from schemas.token import Token
from schemas.user import UserCreate, UserResponse, UserLogin, UserUpdate

settings = get_settings()

# Initialize FastAPI app
app = FastAPI(
    title="Banking REST Service",
    description="A comprehensive banking API with authentication, accounts, transactions, and cards",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Initialize database on startup
@app.on_event("startup")
def startup_event():
    init_database()


def get_current_user(db: Session = Depends(get_database), user_id: int = Depends(verify_token)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# Authentication endpoints
@app.post("/signup", response_model=UserResponse)
def signup(user_create: UserCreate, db: Session = Depends(get_database)):
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_create.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create new user
    hashed_password = get_password_hash(user_create.password)
    user = User(
        email=user_create.email,
        hashed_password=hashed_password,
        full_name=user_create.full_name,
        phone_number=user_create.phone_number
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@app.post("/login", response_model=Token)
def login(user_login: UserLogin, db: Session = Depends(get_database)):
    user = db.query(User).filter(User.email == user_login.email).first()
    if not user or not verify_password(user_login.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}


# Account Holder endpoints
@app.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user


@app.put("/me", response_model=UserResponse)
def update_current_user(
        user_update: UserUpdate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_database)
):
    if user_update.full_name:
        current_user.full_name = user_update.full_name
    if user_update.phone_number:
        current_user.phone_number = user_update.phone_number

    db.commit()
    db.refresh(current_user)
    return current_user


# Account endpoints
@app.post("/accounts", response_model=AccountResponse)
def create_account(
        account_create: AccountCreate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_database)
):
    account = Account(
        user_id=current_user.id,
        account_type=account_create.account_type,
        balance=account_create.initial_balance or 0.0
    )

    db.add(account)
    db.commit()
    db.refresh(account)

    return account


@app.get("/accounts", response_model=List[AccountResponse])
def get_user_accounts(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_database)
):
    accounts = db.query(Account).filter(Account.user_id == current_user.id).all()
    return accounts


@app.get("/accounts/{account_id}", response_model=AccountResponse)
def get_account(
        account_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_database)
):
    account = db.query(Account).filter(
        Account.id == account_id,
        Account.user_id == current_user.id
    ).first()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    return account


# Transaction endpoints
@app.post("/accounts/{account_id}/transactions", response_model=TransactionResponse)
def create_transaction(
        account_id: int,
        transaction_create: TransactionCreate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_database)
):
    account = db.query(Account).filter(
        Account.id == account_id,
        Account.user_id == current_user.id
    ).first()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    # Check balance for debit transactions
    if transaction_create.transaction_type == "debit" and account.balance < transaction_create.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")

    # Create transaction
    transaction = Transaction(
        account_id=account_id,
        transaction_type=transaction_create.transaction_type,
        amount=transaction_create.amount,
        description=transaction_create.description
    )

    # Update account balance
    if transaction_create.transaction_type == "credit":
        account.balance += transaction_create.amount
    else:
        account.balance -= transaction_create.amount

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    return transaction


@app.get("/accounts/{account_id}/transactions", response_model=List[TransactionResponse])
def get_account_transactions(
        account_id: int,
        skip: int = 0,
        limit: int = 100,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_database)
):
    account = db.query(Account).filter(
        Account.id == account_id,
        Account.user_id == current_user.id
    ).first()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    transactions = db.query(Transaction).filter(
        Transaction.account_id == account_id
    ).offset(skip).limit(limit).all()

    return transactions


# Money Transfer endpoints
@app.post("/transfers", response_model=TransferResponse)
def create_transfer(
        transfer_create: TransferCreate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_database)
):
    # Get source account
    source_account = db.query(Account).filter(
        Account.id == transfer_create.from_account_id,
        Account.user_id == current_user.id
    ).first()

    if not source_account:
        raise HTTPException(status_code=404, detail="Source account not found")

    # Get destination account
    dest_account = db.query(Account).filter(
        Account.id == transfer_create.to_account_id
    ).first()

    if not dest_account:
        raise HTTPException(status_code=404, detail="Destination account not found")

    # Check balance
    if source_account.balance < transfer_create.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")

    # Create transfer record
    transfer = Transfer(
        from_account_id=transfer_create.from_account_id,
        to_account_id=transfer_create.to_account_id,
        amount=transfer_create.amount,
        description=transfer_create.description
    )

    # Update balances
    source_account.balance -= transfer_create.amount
    dest_account.balance += transfer_create.amount

    # Create transaction records
    debit_transaction = Transaction(
        account_id=transfer_create.from_account_id,
        transaction_type=TransactionType.DEBIT.value,
        amount=transfer_create.amount,
        description=f"Transfer to account {transfer_create.to_account_id}: {transfer_create.description}"
    )

    credit_transaction = Transaction(
        account_id=transfer_create.to_account_id,
        transaction_type=TransactionType.CREDIT.value,
        amount=transfer_create.amount,
        description=f"Transfer from account {transfer_create.from_account_id}: {transfer_create.description}"
    )

    db.add_all([transfer, debit_transaction, credit_transaction])
    db.commit()
    db.refresh(transfer)

    return transfer


@app.get("/transfers", response_model=List[TransferResponse])
def get_user_transfers(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_database)
):
    # Get user's account IDs
    user_account_ids = [acc.id for acc in db.query(Account).filter(Account.user_id == current_user.id).all()]

    # Get transfers involving user's accounts
    transfers = db.query(Transfer).filter(
        (Transfer.from_account_id.in_(user_account_ids)) |
        (Transfer.to_account_id.in_(user_account_ids))
    ).all()

    return transfers


# Card endpoints
@app.post("/accounts/{account_id}/cards", response_model=CardResponse)
def create_card(
        account_id: int,
        card_create: CardCreate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_database)
):
    account = db.query(Account).filter(
        Account.id == account_id,
        Account.user_id == current_user.id
    ).first()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    # Generate card number (simplified)
    import random
    card_number = f"4{random.randint(100000000000000, 999999999999999)}"

    card = Card(
        account_id=account_id,
        card_number=card_number,
        card_type=card_create.card_type,
        credit_limit=card_create.credit_limit
    )

    db.add(card)
    db.commit()
    db.refresh(card)

    return card


@app.get("/accounts/{account_id}/cards", response_model=List[CardResponse])
def get_account_cards(
        account_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_database)
):
    account = db.query(Account).filter(
        Account.id == account_id,
        Account.user_id == current_user.id
    ).first()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    cards = db.query(Card).filter(Card.account_id == account_id).all()
    return cards


# Statement endpoints
@app.get("/accounts/{account_id}/statements", response_model=List[TransactionResponse])
def get_account_statement(
        account_id: int,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_database)
):
    account = db.query(Account).filter(
        Account.id == account_id,
        Account.user_id == current_user.id
    ).first()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    query = db.query(Transaction).filter(Transaction.account_id == account_id)

    if start_date:
        start_dt = datetime.fromisoformat(start_date)
        query = query.filter(Transaction.timestamp >= start_dt)

    if end_date:
        end_dt = datetime.fromisoformat(end_date)
        query = query.filter(Transaction.timestamp <= end_dt)

    transactions = query.order_by(Transaction.timestamp.desc()).all()
    return transactions


# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
