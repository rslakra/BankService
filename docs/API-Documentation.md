# Banking REST API Documentation

## Base URL
```
http://localhost:8000
```

## Authentication
The API uses JWT Bearer token authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## Response Format
All API responses follow a consistent JSON format:

**Success Response:**
```json
{
  "id": 1,
  "field1": "value1",
  "field2": "value2"
}
```

**Error Response:**
```json
{
  "detail": "Error message description"
}
```

## Endpoints

### Authentication

#### POST /signup
Create a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "full_name": "John Doe",
  "phone_number": "+1234567890"
}
```

**Response (201):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "phone_number": "+1234567890",
  "is_active": true,
  "created_at": "2025-08-23T10:30:00"
}
```

**Errors:**
- `400`: Email already registered
- `422`: Validation error (password too short, invalid email format)

---

#### POST /login
Authenticate user and receive JWT token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Errors:**
- `401`: Invalid credentials

---

### User Management

#### GET /me
Get current user information.

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "phone_number": "+1234567890",
  "is_active": true,
  "created_at": "2025-08-23T10:30:00"
}
```

**Errors:**
- `401`: Invalid or expired token
- `404`: User not found

---

#### PUT /me
Update current user information.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "full_name": "John Smith",
  "phone_number": "+1987654321"
}
```

**Response (200):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Smith",
  "phone_number": "+1987654321",
  "is_active": true,
  "created_at": "2025-08-23T10:30:00"
}
```

---

### Account Management

#### POST /accounts
Create a new bank account.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "account_type": "checking",
  "initial_balance": 1000.0
}
```

**Account Types:** `checking`, `savings`, `business`

**Response (200):**
```json
{
  "id": 1,
  "account_number": "1234567890",
  "account_type": "checking",
  "balance": 1000.0,
  "is_active": true,
  "created_at": "2025-08-23T10:30:00"
}
```

---

#### GET /accounts
Get all user accounts.

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
[
  {
    "id": 1,
    "account_number": "1234567890",
    "account_type": "checking",
    "balance": 1000.0,
    "is_active": true,
    "created_at": "2025-08-23T10:30:00"
  },
  {
    "id": 2,
    "account_number": "0987654321",
    "account_type": "savings",
    "balance": 500.0,
    "is_active": true,
    "created_at": "2025-08-23T10:35:00"
  }
]
```

---

#### GET /accounts/{account_id}
Get specific account details.

**Headers:** `Authorization: Bearer <token>`

**Path Parameters:**
- `account_id` (integer): Account ID

**Response (200):**
```json
{
  "id": 1,
  "account_number": "1234567890",
  "account_type": "checking",
  "balance": 1000.0,
  "is_active": true,
  "created_at": "2025-08-23T10:30:00"
}
```

**Errors:**
- `404`: Account not found or not owned by user

---

### Transaction Management

#### POST /accounts/{account_id}/transactions
Create a new transaction.

**Headers:** `Authorization: Bearer <token>`

**Path Parameters:**
- `account_id` (integer): Account ID

**Request Body:**
```json
{
  "transaction_type": "credit",
  "amount": 500.0,
  "description": "Salary deposit"
}
```

**Transaction Types:** `credit`, `debit`

**Response (200):**
```json
{
  "id": 1,
  "account_id": 1,
  "transaction_type": "credit",
  "amount": 500.0,
  "description": "Salary deposit",
  "reference_number": "TXN-550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2025-08-23T10:45:00"
}
```

**Errors:**
- `400`: Insufficient funds (for debit transactions)
- `404`: Account not found
- `422`: Invalid amount (negative or zero)

---

#### GET /accounts/{account_id}/transactions
Get account transactions.

**Headers:** `Authorization: Bearer <token>`

**Path Parameters:**
- `account_id` (integer): Account ID

**Query Parameters:**
- `skip` (integer, optional): Number of transactions to skip (default: 0)
- `limit` (integer, optional): Maximum number of transactions (default: 100)

**Response (200):**
```json
[
  {
    "id": 1,
    "account_id": 1,
    "transaction_type": "credit",
    "amount": 500.0,
    "description": "Salary deposit",
    "reference_number": "TXN-550e8400-e29b-41d4-a716-446655440000",
    "timestamp": "2025-08-23T10:45:00"
  },
  {
    "id": 2,
    "account_id": 1,
    "transaction_type": "debit",
    "amount": 100.0,
    "description": "ATM withdrawal",
    "reference_number": "TXN-660f9500-f30c-52e5-b827-557766551111",
    "timestamp": "2025-08-23T11:00:00"
  }
]
```

---

### Money Transfers

#### POST /transfers
Transfer money between accounts.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "from_account_id": 1,
  "to_account_id": 2,
  "amount": 200.0,
  "description": "Transfer to savings"
}
```

**Response (200):**
```json
{
  "id": 1,
  "from_account_id": 1,
  "to_account_id": 2,
  "amount": 200.0,
  "description": "Transfer to savings",
  "reference_number": "TRF-770g0600-g41d-63f6-c938-668877662222",
  "timestamp": "2025-08-23T11:15:00"
}
```

**Errors:**
- `400`: Insufficient funds, same account transfer
- `404`: Source or destination account not found
- `422`: Invalid amount or account IDs

---

#### GET /transfers
Get user transfer history.

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
[
  {
    "id": 1,
    "from_account_id": 1,
    "to_account_id": 2,
    "amount": 200.0,
    "description": "Transfer to savings",
    "reference_number": "TRF-770g0600-g41d-63f6-c938-668877662222",
    "timestamp": "2025-08-23T11:15:00"
  }
]
```

---

### Card Management

#### POST /accounts/{account_id}/cards
Create a new card for an account.

**Headers:** `Authorization: Bearer <token>`

**Path Parameters:**
- `account_id` (integer): Account ID

**Request Body:**
```json
{
  "card_type": "debit",
  "credit_limit": 0.0
}
```

**Card Types:** `debit`, `credit`

**Response (200):**
```json
{
  "id": 1,
  "account_id": 1,
  "card_number": "4123456789012345",
  "card_type": "debit",
  "status": "active",
  "credit_limit": 0.0,
  "expiry_date": "2029-08-23T00:00:00",
  "created_at": "2025-08-23T11:30:00"
}
```

**Note:** CVV is generated but not returned in API responses for security.

---

#### GET /accounts/{account_id}/cards
Get all cards for an account.

**Headers:** `Authorization: Bearer <token>`

**Path Parameters:**
- `account_id` (integer): Account ID

**Response (200):**
```json
[
  {
    "id": 1,
    "account_id": 1,
    "card_number": "4123456789012345",
    "card_type": "debit",
    "status": "active",
    "credit_limit": 0.0,
    "expiry_date": "2029-08-23T00:00:00",
    "created_at": "2025-08-23T11:30:00"
  },
  {
    "id": 2,
    "account_id": 1,
    "card_number": "4987654321098765",
    "card_type": "credit",
    "status": "active",
    "credit_limit": 5000.0,
    "expiry_date": "2029-08-23T00:00:00",
    "created_at": "2025-08-23T11:35:00"
  }
]
```

---

### Statements

#### GET /accounts/{account_id}/statements
Get account statement (transaction history with optional date filtering).

**Headers:** `Authorization: Bearer <token>`

**Path Parameters:**
- `account_id` (integer): Account ID

**Query Parameters:**
- `start_date` (string, optional): Start date in ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)
- `end_date` (string, optional): End date in ISO format

**Example:** `/accounts/1/statements?start_date=2025-08-01&end_date=2025-08-31`

**Response (200):**
```json
[
  {
    "id": 3,
    "account_id": 1,
    "transaction_type": "credit",
    "amount": 500.0,
    "description": "Salary deposit",
    "reference_number": "TXN-550e8400-e29b-41d4-a716-446655440000",
    "timestamp": "2025-08-23T10:45:00"
  },
  {
    "id": 2,
    "account_id": 1,
    "transaction_type": "debit",
    "amount": 200.0,
    "description": "Transfer to account 2: Transfer to savings",
    "reference_number": "TXN-661g0500-g42e-64g7-d949-669988773333",
    "timestamp": "2025-08-23T11:15:00"
  }
]
```

---

### Health Check

#### GET /health
Check API service health (no authentication required).

**Response (200):**
```json
{
  "status": "healthy",
  "timestamp": "2025-08-23T12:00:00"
}
```

---

## HTTP Status Codes

| Code | Description                             |
|------|-----------------------------------------|
| 200  | OK - Request successful                 |
| 201  | Created - Resource created successfully |
| 400  | Bad Request - Invalid request data      |
| 401  | Unauthorized - Invalid or missing token |
| 403  | Forbidden - Access denied               |
| 404  | Not Found - Resource not found          |
| 422  | Unprocessable Entity - Validation error |
| 500  | Internal Server Error - Server error    |

## Rate Limiting
Currently, no rate limiting is implemented. In production, consider implementing:
- 5 requests per minute for login endpoint
- 100 requests per minute for authenticated endpoints
- 1000 requests per hour per user

## Data Types and Constraints

### Account Types
- `CHECKING`: Standard checking account
- `SAVINGS`: Savings account
- `BUSINESS`: Business account

### Transaction Types
- `CREDIT`: Money added to account (deposits, transfers in)
- `DEBIT`: Money removed from account (withdrawals, transfers out)

### Card Types
- `DEBIT`: Debit card linked to account balance
- `CREDIT`: Credit card with credit limit

### Card Status
- `ACTIVE`: Card is active and can be used
- `BLOCKED`: Card is temporarily blocked
- `EXPIRED`: Card has expired

### Validation Rules
- **Email**: Must be valid email format
- **Password**: Minimum 8 characters
- **Amount**: Must be positive number
- **Phone**: Optional, any format accepted
- **Account Numbers**: Auto-generated, 10 digits
- **Card Numbers**: Auto-generated, 16 digits starting with 4

## Interactive Documentation
Visit `http://localhost:8000/docs` for interactive Swagger UI documentation where you can test all endpoints directly in your browser.

Alternative documentation is available at `http://localhost:8000/redoc` for a different viewing experience.

## Example Workflows

### Complete Banking Workflow
1. **Sign up**: `POST /signup`
2. **Login**: `POST /login` (get token)
3. **Create accounts**: `POST /accounts` (checking and savings)
4. **Make deposit**: `POST /accounts/{id}/transactions` (credit)
5. **Transfer money**: `POST /transfers`
6. **Create card**: `POST /accounts/{id}/cards`
7. **Get statement**: `GET /accounts/{id}/statements`

### Error Handling Example
```bash
# Request without authentication
curl -X GET "http://localhost:8000/me"

# Response
{
  "detail": "Not authenticated"
}

# Request with invalid token
curl -X GET "http://localhost:8000/me" \
     -H "Authorization: Bearer invalid_token"

# Response
{
  "detail": "Invalid token"
}
```

This documentation provides comprehensive information for integrating with the Banking REST API. For additional support or questions, refer to the source code or contact the development team.
