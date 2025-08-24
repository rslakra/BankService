# Banking REST Service - Solution Documentation

## Overview
This is a comprehensive Banking REST API built with FastAPI, featuring authentication, account management, transactions, money transfers, cards, and statements. The service uses SQLite for data persistence and includes comprehensive unit tests.

## Technology Stack
- **Framework**: FastAPI (modern, fast Python web framework)
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: JWT tokens with bcrypt password hashing
- **Validation**: Pydantic models for request/response validation
- **Testing**: pytest with comprehensive unit and integration tests
- **Documentation**: Auto-generated OpenAPI/Swagger documentation

## Project Structure
```text
BankService/
├── config/
│   ├── __init__.py
│   ├── base.py
│   └── /
├── core/
│   ├── enums/
│   ├── __init__.py
│   ├── base.py
│   ├── database.py             # Database configuration
│   ├── logger.py
│   ├── security.py
│   └── /
├── docs/
│   ├── AI-UsageReport.md               # AI development process
│   ├── API-Documentation.md            # REST API Documentation
│   ├── SecurityConsiderations.md       # Security considerations
│   ├── Solution.md                     # Setup and deployment guide
│   └── /
├── models/                     # SQLAlchemy database models
│   ├── __init__.py
│   ├── account.py
│   ├── card.py
│   ├── user.py
│   └── /
├── schemas/                    # Pydantic request/response schemas
│   ├── __init__.py
│   ├── account.py
│   ├── base.py
│   ├── token.py
│   ├── user.py
│   └── /
├── tests/                          # Comprehensive unit tests
│   ├── __init__.py
│   ├── base.py
│   ├── test_account.py
│   ├── test_user.py
│   └── /
├── .gitignore
├── demo_client.py                  # Interactive demo application
├── docker-compose.yml              # Multi-service orchestration
├── Dockerfile                      # Container configuration
├── main.py                         # FastAPI application & API endpoints
├── Makefile                        # Makefile
├── pytest.ini                      # Test configuration
├── README.md
├── requirements.txt                # Python dependencies
├── sample.env                      # Sample .env file
└── /
```

## Local development

- Create a virtual environment:

```
python3 -m pip install virtualenv
python3 -m venv venv
. ./venv/bin/activate
```

- Install requirements:

```
pip install --upgrade pip
pip install -r ./requirements.txt
```

**Note: - Setup Application Environment**

By default, ```.env``` file is loaded but if your application points to any other env for example **production**, then *
*make sure one of the criteria meets**:

- Either ```.env``` file contains the **production** specific configs, OR
- ```.env.<APP_ENV>``` file exists (i.e. for production, file name = .env.production) and contains the **production**
  specific configs


## Docker development

- List all make file commands

```shell
make
```

- Build docker image

```shell
make build-container

OR

make build-container service=bank-service tag=v0.0.1
```

- Run docker container

```shell
make run-container

OR

make run-container service=bank-service tag=v0.0.1
```

- stop docker image

```shell
make stop-container

OR

make stop-container service=bank-service
```

```

- Check container logs
```shell
make log-container

OR

make log-container service=bank-service
```

- Connect as a 'bash' shell in the container

```shell
make bash-container

OR

make bash-container service=bank
```



## Setup Instructions

### 1. Prerequisites
- Python 3.10 or higher
- pip (Python package manager)

### 2. Installation
```bash
# Clone or extract the project
cd banking-service

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Running the Application
```bash
# Start the server
python main.py

# Or using uvicorn directly:
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **Base URL**: http://localhost:8000
- **Interactive API Documentation**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc

### 4. Running Tests
```bash
# Run all tests
pytest test_main.py -v

# Run tests with coverage
pytest test_main.py -v --cov=main

# Run specific test class
pytest test_main.py::TestAuth -v
```

## API Endpoints

### Authentication
- `POST /signup` - Create new user account
- `POST /login` - Authenticate and get JWT token

### User Management
- `GET /me` - Get current user information
- `PUT /me` - Update current user information

### Account Management
- `POST /accounts` - Create new account
- `GET /accounts` - Get all user accounts
- `GET /accounts/{account_id}` - Get specific account

### Transactions
- `POST /accounts/{account_id}/transactions` - Create new transaction
- `GET /accounts/{account_id}/transactions` - Get account transactions

### Money Transfers
- `POST /transfers` - Transfer money between accounts
- `GET /transfers` - Get user transfers

### Cards
- `POST /accounts/{account_id}/cards` - Create new card
- `GET /accounts/{account_id}/cards` - Get account cards

### Statements
- `GET /accounts/{account_id}/statements` - Get account statements

### Health Check
- `GET /health` - Check service health

## Usage Examples

### 1. User Registration and Login
```bash
# Register new user
curl -X POST "http://localhost:8000/signup" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "john@example.com",
       "password": "securepassword123",
       "full_name": "John Doe",
       "phone_number": "+1234567890"
     }'

# Login to get token
curl -X POST "http://localhost:8000/login" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "john@example.com",
       "password": "securepassword123"
     }'
```

### 2. Create Account
```bash
# Create checking account (use token from login)
curl -X POST "http://localhost:8000/accounts" \
     -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     -H "Content-Type: application/json" \
     -d '{
       "account_type": "checking",
       "initial_balance": 1000.0
     }'
```

### 3. Make Transaction
```bash
# Make a deposit
curl -X POST "http://localhost:8000/accounts/1/transactions" \
     -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     -H "Content-Type: application/json" \
     -d '{
       "transaction_type": "credit",
       "amount": 500.0,
       "description": "Salary deposit"
     }'
```

### 4. Transfer Money
```bash
# Transfer between accounts
curl -X POST "http://localhost:8000/transfers" \
     -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     -H "Content-Type: application/json" \
     -d '{
       "from_account_id": 1,
       "to_account_id": 2,
       "amount": 200.0,
       "description": "Transfer to savings"
     }'
```

## Security Features

### Authentication & Authorization
- JWT-based authentication with secure token generation
- Password hashing using bcrypt with salt
- Protected endpoints requiring valid authentication
- User isolation - users can only access their own data

### Data Validation
- Comprehensive input validation using Pydantic
- Email format validation
- Password strength requirements (minimum 8 characters)
- Amount validation (positive values only)
- Account ownership verification for all operations

### Database Security
- SQL injection protection through SQLAlchemy ORM
- Parameterized queries for all database operations
- Secure password storage (never stored in plain text)

## Database Schema

### Users Table
- `id`: Primary key
- `email`: Unique email address
- `hashed_password`: Bcrypt hashed password
- `full_name`: User's full name
- `phone_number`: Contact number
- `is_active`: Account status
- `created_at`, `updated_at`: Timestamps

### Accounts Table
- `id`: Primary key
- `user_id`: Foreign key to Users
- `account_number`: Unique account identifier
- `account_type`: checking, savings, or business
- `balance`: Current account balance
- `is_active`: Account status
- `created_at`, `updated_at`: Timestamps

### Transactions Table
- `id`: Primary key
- `account_id`: Foreign key to Accounts
- `transaction_type`: credit or debit
- `amount`: Transaction amount
- `description`: Transaction description
- `reference_number`: Unique transaction reference
- `timestamp`: Transaction timestamp

### Transfers Table
- `id`: Primary key
- `from_account_id`: Source account
- `to_account_id`: Destination account
- `amount`: Transfer amount
- `description`: Transfer description
- `reference_number`: Unique transfer reference
- `timestamp`: Transfer timestamp

### Cards Table
- `id`: Primary key
- `account_id`: Foreign key to Accounts
- `card_number`: Unique card number
- `card_type`: debit or credit
- `status`: active, blocked, or expired
- `credit_limit`: Credit limit (for credit cards)
- `expiry_date`: Card expiration date
- `cvv`: Card verification value
- `created_at`, `updated_at`: Timestamps

## Testing Strategy

### Unit Tests
- Authentication flow testing
- User management operations
- Account CRUD operations
- Transaction processing
- Transfer functionality
- Card management
- Statement generation
- Error handling and edge cases

### Integration Tests
- Complete banking workflow
- Multi-step operations
- Balance verification
- Data consistency checks

### Test Coverage
- All critical business logic
- Error scenarios
- Authorization checks
- Input validation

## Performance Considerations

### Database Optimization
- Proper indexing on frequently queried fields
- Efficient foreign key relationships
- Connection pooling for concurrent requests

### API Performance
- Async/await support for I/O operations
- Efficient JWT token validation
- Minimal database queries per request

## Production Deployment Considerations

### Environment Variables
```bash
SECRET_KEY=your-super-secret-key-change-this-in-production
DATABASE_URL=sqlite:///./banking.db
```

### Security Enhancements for Production
1. Use a stronger SECRET_KEY (32+ random characters)
2. Implement rate limiting
3. Add HTTPS/TLS encryption
4. Use PostgreSQL or MySQL instead of SQLite
5. Implement audit logging
6. Add request validation middleware
7. Set up monitoring and alerting

### Scaling Considerations
1. Database connection pooling
2. Caching layer (Redis)
3. Load balancing
4. Database read replicas
5. Microservices architecture for large scale

## Troubleshooting

### Common Issues
1. **Database locked**: Ensure only one instance is running
2. **Token expired**: Re-authenticate to get new token
3. **Permission denied**: Check user owns the resource
4. **Insufficient funds**: Verify account balance before transactions

### Logs
Check console output for detailed error messages and request logs.

## Future Enhancements
1. Account statements in PDF format
2. Transaction categorization
3. Scheduled transfers
4. Multi-currency support
5. Mobile push notifications
6. Two-factor authentication
7. Transaction limits and rules
8. Fraud detection algorithms


# Reference

- [The Python Package Index (PyPI)](https://pypi.org/)
- Gemini AI
- 