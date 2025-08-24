# demo_client.py
"""
Demo client application to showcase the Banking REST API functionality
"""
from typing import Dict

import requests


class BankingAPIClient:
    """Banking REST API Client"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.token = None
        self.headers = {"Content-Type": "application/json"}

    def _make_request(self, method: str, endpoint: str, data: Dict = None, auth_required: bool = True):
        """Make HTTP request with error handling"""
        url = f"{self.base_url}{endpoint}"
        headers = self.headers.copy()

        if auth_required and self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        try:
            if method == "GET":
                response = requests.get(url, headers=headers)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data)
            elif method == "PUT":
                response = requests.put(url, headers=headers, json=data)

            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            return None

    def signup(self, user_data: Dict):
        """Register a new user"""
        print("\n🔐 Creating new user account...")
        result = self._make_request("POST", "/signup", user_data, auth_required=False)
        if result:
            print(f"✅ User created successfully: {result['email']}")
        return result

    def login(self, email: str, password: str):
        """Login and get access token"""
        print(f"\n🔑 Logging in as {email}...")
        result = self._make_request("POST", "/login",
                                    {"email": email, "password": password},
                                    auth_required=False)
        if result:
            self.token = result["access_token"]
            print("✅ Login successful!")
        return result

    def get_profile(self):
        """Get current user profile"""
        print("\n👤 Getting user profile...")
        result = self._make_request("GET", "/me")
        if result:
            print(f"✅ Profile: {result['full_name']} ({result['email']})")
        return result

    def create_account(self, account_type: str, initial_balance: float = 0.0):
        """Create a new bank account"""
        print(f"\n🏦 Creating {account_type} account with ${initial_balance}...")
        result = self._make_request("POST", "/accounts", {
            "account_type": account_type,
            "initial_balance": initial_balance
        })
        if result:
            print(f"✅ Account created: #{result['account_number']} (ID: {result['id']})")
        return result

    def get_accounts(self):
        """Get all user accounts"""
        print("\n📊 Getting all accounts...")
        result = self._make_request("GET", "/accounts")
        if result:
            print(f"✅ Found {len(result)} accounts:")
            for account in result:
                print(f"   - {account['account_type'].title()} #{account['account_number']}: ${account['balance']}")
        return result

    def create_transaction(self, account_id: int, transaction_type: str, amount: float, description: str):
        """Create a new transaction"""
        print(f"\n💰 Creating {transaction_type} transaction of ${amount}...")
        result = self._make_request("POST", f"/accounts/{account_id}/transactions", {
            "transaction_type": transaction_type,
            "amount": amount,
            "description": description
        })
        if result:
            print(f"✅ Transaction created: {result['reference_number']}")
        return result

    def transfer_money(self, from_account_id: int, to_account_id: int, amount: float, description: str):
        """Transfer money between accounts"""
        print(f"\n🔄 Transferring ${amount} from account {from_account_id} to {to_account_id}...")
        result = self._make_request("POST", "/transfers", {
            "from_account_id": from_account_id,
            "to_account_id": to_account_id,
            "amount": amount,
            "description": description
        })
        if result:
            print(f"✅ Transfer completed: {result['reference_number']}")
        return result

    def create_card(self, account_id: int, card_type: str, credit_limit: float = 0.0):
        """Create a new card for an account"""
        print(f"\n💳 Creating {card_type} card for account {account_id}...")
        result = self._make_request("POST", f"/accounts/{account_id}/cards", {
            "card_type": card_type,
            "credit_limit": credit_limit
        })
        if result:
            print(f"✅ Card created: {result['card_number'][:4]}****{result['card_number'][-4:]}")
        return result

    def get_account_cards(self, account_id: int):
        """Get all cards for an account"""
        print(f"\n💳 Getting cards for account {account_id}...")
        result = self._make_request("GET", f"/accounts/{account_id}/cards")
        if result:
            print(f"✅ Found {len(result)} cards:")
            for card in result:
                masked_number = f"{card['card_number'][:4]}****{card['card_number'][-4:]}"
                print(f"   - {card['card_type'].title()}: {masked_number} (Status: {card['status']})")
        return result

    def get_account_statement(self, account_id: int):
        """Get account statement"""
        print(f"\n📄 Getting statement for account {account_id}...")
        result = self._make_request("GET", f"/accounts/{account_id}/statements")
        if result:
            print(f"✅ Found {len(result)} transactions:")
            for txn in result:
                sign = "+" if txn['transaction_type'] == 'credit' else "-"
                print(f"   - {txn['timestamp'][:19]}: {sign}${txn['amount']} - {txn['description']}")
        return result

    def get_transfers(self):
        """Get all user transfers"""
        print("\n🔄 Getting transfer history...")
        result = self._make_request("GET", "/transfers")
        if result:
            print(f"✅ Found {len(result)} transfers:")
            for transfer in result:
                print(
                    f"   - {transfer['timestamp'][:19]}: ${transfer['amount']} from {transfer['from_account_id']} to {transfer['to_account_id']}")
        return result

    def health_check(self):
        """Check API health"""
        print("\n❤️ Checking API health...")
        result = self._make_request("GET", "/health", auth_required=False)
        if result:
            print(f"✅ API is healthy - Status: {result['status']}")
        return result


def demo_banking_workflow():
    """Demonstrate complete banking workflow"""
    print("🏦 Banking REST API Demo")
    print("=" * 50)

    # Initialize client
    client = BankingAPIClient()

    # Check API health
    if not client.health_check():
        print("❌ API is not responding. Make sure the server is running!")
        return

    # User data for demo
    user_data = {
        "email": "demo@bankingapi.com",
        "password": "SecureDemo123!",
        "full_name": "Demo User",
        "phone_number": "+1-555-0123"
    }

    # 1. Create user account
    if not client.signup(user_data):
        print("⚠️ User might already exist, trying to login...")

    # 2. Login
    if not client.login(user_data["email"], user_data["password"]):
        return

    # 3. Get user profile
    client.get_profile()

    # 4. Create accounts
    checking_account = client.create_account("checking", 2500.00)
    if not checking_account:
        return

    savings_account = client.create_account("savings", 1000.00)
    if not savings_account:
        return

    business_account = client.create_account("business", 5000.00)
    if not business_account:
        return

    # 5. View all accounts
    client.get_accounts()

    # 6. Make some transactions
    print("\n" + "=" * 50)
    print("💰 TRANSACTION DEMONSTRATIONS")
    print("=" * 50)

    # Deposit to checking
    client.create_transaction(
        checking_account["id"],
        "credit",
        1250.00,
        "Salary deposit"
    )

    # Withdrawal from checking
    client.create_transaction(
        checking_account["id"],
        "debit",
        150.00,
        "ATM withdrawal"
    )

    # Deposit to savings
    client.create_transaction(
        savings_account["id"],
        "credit",
        500.00,
        "Monthly savings"
    )

    # Business income
    client.create_transaction(
        business_account["id"],
        "credit",
        2000.00,
        "Client payment"
    )

    # 7. Transfer money between accounts
    print("\n" + "=" * 50)
    print("🔄 MONEY TRANSFER DEMONSTRATIONS")
    print("=" * 50)

    # Transfer from checking to savings
    client.transfer_money(
        checking_account["id"],
        savings_account["id"],
        750.00,
        "Emergency fund contribution"
    )

    # Transfer from business to checking
    client.transfer_money(
        business_account["id"],
        checking_account["id"],
        1500.00,
        "Owner salary transfer"
    )

    # 8. Create cards
    print("\n" + "=" * 50)
    print("💳 CARD MANAGEMENT DEMONSTRATIONS")
    print("=" * 50)

    # Debit card for checking account
    client.create_card(checking_account["id"], "debit")

    # Credit card for checking account
    client.create_card(checking_account["id"], "credit", 3000.00)

    # Business debit card
    client.create_card(business_account["id"], "debit")

    # View cards for checking account
    client.get_account_cards(checking_account["id"])

    # 9. Generate statements
    print("\n" + "=" * 50)
    print("📄 ACCOUNT STATEMENTS")
    print("=" * 50)

    print(f"\n📋 CHECKING ACCOUNT STATEMENT (ID: {checking_account['id']})")
    client.get_account_statement(checking_account["id"])

    print(f"\n📋 SAVINGS ACCOUNT STATEMENT (ID: {savings_account['id']})")
    client.get_account_statement(savings_account["id"])

    print(f"\n📋 BUSINESS ACCOUNT STATEMENT (ID: {business_account['id']})")
    client.get_account_statement(business_account["id"])

    # 10. View transfer history
    print("\n" + "=" * 50)
    print("🔄 TRANSFER HISTORY")
    print("=" * 50)
    client.get_transfers()

    # 11. Final account balances
    print("\n" + "=" * 50)
    print("📊 FINAL ACCOUNT BALANCES")
    print("=" * 50)
    client.get_accounts()

    print("\n" + "=" * 50)
    print("🎉 DEMO COMPLETED SUCCESSFULLY!")
    print("=" * 50)
    print("\nKey features demonstrated:")
    print("✅ User registration and authentication")
    print("✅ Multiple account types (checking, savings, business)")
    print("✅ Credit and debit transactions")
    print("✅ Money transfers between accounts")
    print("✅ Debit and credit card creation")
    print("✅ Account statements and transaction history")
    print("✅ Transfer history tracking")
    print("✅ Real-time balance updates")
    print("\nCheck the interactive API docs at: http://localhost:8000/docs")


def demo_error_scenarios():
    """Demonstrate error handling scenarios"""
    print("\n" + "=" * 50)
    print("⚠️ ERROR SCENARIO DEMONSTRATIONS")
    print("=" * 50)

    client = BankingAPIClient()

    # 1. Try accessing protected endpoint without auth
    print("\n🚫 Attempting to access protected endpoint without authentication:")
    client.get_profile()

    # Login first
    user_data = {
        "email": "demo@bankingapi.com",
        "password": "SecureDemo123!"
    }
    client.login(user_data["email"], user_data["password"])

    # Get an account to work with
    accounts = client.get_accounts()
    if accounts and len(accounts) > 0:
        account_id = accounts[0]["id"]

        # 2. Try insufficient funds transaction
        print("\n💸 Attempting withdrawal with insufficient funds:")
        client.create_transaction(account_id, "debit", 999999.00, "Attempted overdraft")

        # 3. Try invalid transfer (same account)
        print("\n🔄 Attempting transfer to same account:")
        client._make_request("POST", "/transfers", {
            "from_account_id": account_id,
            "to_account_id": account_id,
            "amount": 100.00,
            "description": "Invalid self-transfer"
        })

        # 4. Try negative amount transaction
        print("\n➖ Attempting negative amount transaction:")
        client._make_request("POST", f"/accounts/{account_id}/transactions", {
            "transaction_type": "credit",
            "amount": -100.00,
            "description": "Invalid negative amount"
        })

    print("\n✅ Error scenarios demonstration completed!")


if __name__ == "__main__":
    print("Starting Banking API Demo...")
    print("Make sure the API server is running on http://localhost:8000")
    print("\nPress Enter to start the demo, or Ctrl+C to exit...")

    try:
        input()
        demo_banking_workflow()

        print("\n" + "=" * 50)
        print("Would you like to see error scenario demonstrations? (y/n)")
        if input().lower().startswith('y'):
            demo_error_scenarios()

    except KeyboardInterrupt:
        print("\n\n👋 Demo cancelled. Goodbye!")
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        print("Make sure the API server is running and accessible.")
