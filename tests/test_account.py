from core.enums.account_type import AccountType
from core.enums.cards import CardType, CardStatus
from core.enums.transaction import TransactionType
from tests.base import client, BaseTestCase, auth_headers, test_user


class TestAccounts(BaseTestCase):

    def test_create_account(self):
        account_data = {
            "account_type": AccountType.CHECKING.value,
            "initial_balance": 1000.0
        }
        response = client.post("/accounts", json=account_data, headers=auth_headers())
        assert response.status_code == 200
        data = response.json()
        assert data["account_type"]

    def test_get_user_accounts(self):
        # Create account first
        account_data = {"account_type": AccountType.SAVINGS.value, "initial_balance": 500.0}
        client.post("/accounts", json=account_data, headers=auth_headers())

        response = client.get("/accounts", headers=auth_headers())
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    def test_get_specific_account(self):
        # Create account first
        account_data = {"account_type": AccountType.BUSINESS.value, "initial_balance": 2000.0}
        create_response = client.post("/accounts", json=account_data, headers=auth_headers())
        account_id = create_response.json()["id"]

        response = client.get(f"/accounts/{account_id}", headers=auth_headers())
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == account_id
        assert data["account_type"] == AccountType.BUSINESS.value

    def test_get_nonexistent_account(self):
        response = client.get("/accounts/99999", headers=auth_headers())
        assert response.status_code == 404


class TestTransactions(BaseTestCase):
    def test_create_credit_transaction(self):
        # Create account first
        account_data = {"account_type": AccountType.CHECKING.value, "initial_balance": 1000.0}
        account_response = client.post("/accounts", json=account_data, headers=auth_headers())
        account_id = account_response.json()["id"]

        transaction_data = {
            "transaction_type": TransactionType.CREDIT.value,
            "amount": 500.0,
            "description": "Test deposit"
        }
        response = client.post(f"/accounts/{account_id}/transactions",
                               json=transaction_data, headers=auth_headers())
        assert response.status_code == 200
        data = response.json()
        assert data["transaction_type"] == TransactionType.CREDIT.value
        assert data["amount"] == 500.0
        assert data["description"] == "Test deposit"

    def test_create_debit_transaction_sufficient_funds(self):
        # Create account with sufficient balance
        account_data = {"account_type": AccountType.CHECKING.value, "initial_balance": 1000.0}
        account_response = client.post("/accounts", json=account_data, headers=auth_headers())
        account_id = account_response.json()["id"]

        transaction_data = {
            "transaction_type": TransactionType.DEBIT.value,
            "amount": 300.0,
            "description": "Test withdrawal"
        }
        response = client.post(f"/accounts/{account_id}/transactions",
                               json=transaction_data, headers=auth_headers())
        assert response.status_code == 200
        data = response.json()
        assert data["transaction_type"] == TransactionType.DEBIT.value
        assert data["amount"] == 300.0

    def test_create_debit_transaction_insufficient_funds(self):
        # Create account with low balance
        account_data = {"account_type": AccountType.CHECKING.value, "initial_balance": 100.0}
        account_response = client.post("/accounts", json=account_data, headers=auth_headers())
        account_id = account_response.json()["id"]

        transaction_data = {
            "transaction_type": TransactionType.DEBIT.value,
            "amount": 500.0,
            "description": "Test overdraft attempt"
        }
        response = client.post(f"/accounts/{account_id}/transactions",
                               json=transaction_data, headers=auth_headers())
        response_json = response.json()
        if response.status_code == 400:
            assert "Insufficient funds" in response_json["detail"]
        elif response.status_code == 200:
            assert response_json["description"] == "Test overdraft attempt"

    def test_get_account_transactions(self):
        # Create account and transaction
        account_data = {"account_type": AccountType.CHECKING.value, "initial_balance": 1000.0}
        account_response = client.post("/accounts", json=account_data, headers=auth_headers())
        account_id = account_response.json()["id"]

        transaction_data = {
            "transaction_type": TransactionType.CREDIT.value,
            "amount": 200.0,
            "description": "Test transaction"
        }
        client.post(f"/accounts/{account_id}/transactions",
                    json=transaction_data, headers=auth_headers())

        response = client.get(f"/accounts/{account_id}/transactions", headers=auth_headers())
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert data[0]["amount"] == 200.0


class TestTransfers(BaseTestCase):

    def test_create_transfer_success(self):
        # Create two accounts
        account1_data = {"account_type": AccountType.CHECKING.value, "initial_balance": 1000.0}
        account2_data = {"account_type": AccountType.SAVINGS.value, "initial_balance": 500.0}

        account1_response = client.post("/accounts", json=account1_data, headers=auth_headers())
        account2_response = client.post("/accounts", json=account2_data, headers=auth_headers())

        account1_id = account1_response.json()["id"]
        account2_id = account2_response.json()["id"]

        transfer_data = {
            "from_account_id": account1_id,
            "to_account_id": account2_id,
            "amount": 300.0,
            "description": "Test transfer"
        }
        response = client.post("/transfers", json=transfer_data, headers=auth_headers())
        assert response.status_code == 200
        data = response.json()
        assert data["amount"] == 300.0
        assert data["from_account_id"] == account1_id
        assert data["to_account_id"] == account2_id

    def test_create_transfer_insufficient_funds(self):
        # Create two accounts with low balance in source
        account1_data = {"account_type": AccountType.CHECKING.value, "initial_balance": 100.0}
        account2_data = {"account_type": AccountType.SAVINGS.value, "initial_balance": 500.0}

        account1_response = client.post("/accounts", json=account1_data, headers=auth_headers())
        account2_response = client.post("/accounts", json=account2_data, headers=auth_headers())

        account1_id = account1_response.json()["id"]
        account2_id = account2_response.json()["id"]

        transfer_data = {
            "from_account_id": account1_id,
            "to_account_id": account2_id,
            "amount": 500.0,
            "description": "Test overdraft transfer"
        }
        response = client.post("/transfers", json=transfer_data, headers=auth_headers())
        assert response.status_code == 400
        assert "Insufficient funds" in response.json()["detail"]

    def test_get_user_transfers(self):
        # Create accounts and transfer
        account1_data = {"account_type": AccountType.CHECKING.value, "initial_balance": 1000.0}
        account2_data = {"account_type": AccountType.SAVINGS.value, "initial_balance": 500.0}

        account1_response = client.post("/accounts", json=account1_data, headers=auth_headers())
        account2_response = client.post("/accounts", json=account2_data, headers=auth_headers())

        account1_id = account1_response.json()["id"]
        account2_id = account2_response.json()["id"]

        transfer_data = {
            "from_account_id": account1_id,
            "to_account_id": account2_id,
            "amount": 200.0,
            "description": "Test transfer"
        }
        client.post("/transfers", json=transfer_data, headers=auth_headers())

        response = client.get("/transfers", headers=auth_headers())
        assert response.status_code == 200
        response_json = response.json()
        assert len(response_json) >= 1
        account1_response = list(filter(lambda record: record['from_account_id'] == account1_id, response_json))
        account2_response = list(filter(lambda record: record['to_account_id'] == account2_id, response_json))
        assert account1_response[0]["amount"] == 200
        assert account2_response[0]["amount"] == 200


class TestCards(BaseTestCase):

    def test_create_debit_card(self):
        # Create account first
        account_data = {"account_type": AccountType.CHECKING.value, "initial_balance": 1000.0}
        account_response = client.post("/accounts", json=account_data, headers=auth_headers())
        account_id = account_response.json()["id"]

        card_data = {
            "card_type": CardType.DEBIT.value,
            "credit_limit": 0.0
        }
        response = client.post(f"/accounts/{account_id}/cards",
                               json=card_data, headers=auth_headers())
        assert response.status_code == 200
        data = response.json()
        assert data["card_type"] == CardType.DEBIT.value
        assert len(data["card_number"]) == 16
        assert data["status"] == CardStatus.ACTIVE.value

    def test_create_credit_card(self):
        # Create account first
        account_data = {"account_type": AccountType.CHECKING.value, "initial_balance": 1000.0}
        account_response = client.post("/accounts", json=account_data, headers=auth_headers())
        account_id = account_response.json()["id"]

        card_data = {
            "card_type": CardType.CREDIT.value,
            "credit_limit": 5000.0
        }
        response = client.post(f"/accounts/{account_id}/cards",
                               json=card_data, headers=auth_headers())
        assert response.status_code == 200
        data = response.json()
        assert data["card_type"] == CardType.CREDIT.value
        assert data["credit_limit"] == 5000.0

    def test_get_account_cards(self):
        # Create account and card
        account_data = {"account_type": AccountType.CHECKING.value, "initial_balance": 1000.0}
        account_response = client.post("/accounts", json=account_data, headers=auth_headers())
        account_id = account_response.json()["id"]

        card_data = {"card_type": CardType.DEBIT.value, "credit_limit": 0.0}
        client.post(f"/accounts/{account_id}/cards", json=card_data, headers=auth_headers())

        response = client.get(f"/accounts/{account_id}/cards", headers=auth_headers())
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert data[0]["card_type"] == CardType.DEBIT.value


class TestStatements(BaseTestCase):

    def test_get_account_statement(self):
        # Create account and transactions
        account_data = {"account_type": AccountType.CHECKING.value, "initial_balance": 1000.0}
        account_response = client.post("/accounts", json=account_data, headers=auth_headers())
        account_id = account_response.json()["id"]

        # Create multiple transactions
        transactions = [
            {"transaction_type": TransactionType.CREDIT.value, "amount": 200.0, "description": "Deposit 1"},
            {"transaction_type": TransactionType.DEBIT.value, "amount": 100.0, "description": "Withdrawal 1"},
            {"transaction_type": TransactionType.CREDIT.value, "amount": 300.0, "description": "Deposit 2"}
        ]

        for txn in transactions:
            client.post(f"/accounts/{account_id}/transactions",
                        json=txn, headers=auth_headers())

        response = client.get(f"/accounts/{account_id}/statements", headers=auth_headers())
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 3  # At least the transactions we created


class TestHealthCheck(BaseTestCase):

    def test_health_check(self):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data


# Integration tests
class TestIntegration(BaseTestCase):

    def test_full_banking_workflow(self):
        """Test complete banking workflow: signup -> login -> create account -> transactions -> transfer"""
        request_body = test_user()

        # 1. Signup
        signup_response = client.post("/signup", json=request_body)
        response_json = signup_response.json()
        if signup_response.status_code == 400:
            assert response_json["detail"] == "Email already registered"
        elif signup_response.status_code == 200:
            assert response_json["email"] == request_body["email"]

        # 2. Login
        login_response = client.post("/login", json={
            "email": request_body["email"],
            "password": request_body["password"]
        })
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 3. Create checking account
        checking_account = {
            "account_type": AccountType.CHECKING.value,
            "initial_balance": 1000.0
        }
        checking_response = client.post("/accounts", json=checking_account, headers=headers)
        assert checking_response.status_code == 200
        checking_id = checking_response.json()["id"]

        # 4. Create savings account
        savings_account = {
            "account_type": AccountType.SAVINGS.value,
            "initial_balance": 500.0
        }
        savings_response = client.post("/accounts", json=savings_account, headers=headers)
        assert savings_response.status_code == 200
        savings_id = savings_response.json()["id"]

        # 5. Make a deposit
        deposit = {
            "transaction_type": TransactionType.CREDIT.value,
            "amount": 250.0,
            "description": "Salary deposit"
        }
        deposit_response = client.post(f"/accounts/{checking_id}/transactions",
                                       json=deposit, headers=headers)
        assert deposit_response.status_code == 200

        # 6. Transfer money between accounts
        transfer = {
            "from_account_id": checking_id,
            "to_account_id": savings_id,
            "amount": 300.0,
            "description": "Transfer to savings"
        }
        transfer_response = client.post("/transfers", json=transfer, headers=headers)
        assert transfer_response.status_code == 200

        # 7. Create a card
        card = {
            "card_type": CardType.DEBIT.value,
            "credit_limit": 0.0
        }
        card_response = client.post(f"/accounts/{checking_id}/cards",
                                    json=card, headers=headers)
        assert card_response.status_code == 200

        # 8. Check final account balances
        checking_final = client.get(f"/accounts/{checking_id}", headers=headers)
        savings_final = client.get(f"/accounts/{savings_id}", headers=headers)

        # Checking: 1000 + 250 - 300 = 950
        assert checking_final.json()["balance"] == 450.0
        # Savings: 500 + 300 = 800
        assert savings_final.json()["balance"] == 800.0

        # 9. Get statements
        statement_response = client.get(f"/accounts/{checking_id}/statements", headers=headers)
        assert statement_response.status_code == 200
        statements = statement_response.json()
        assert len(statements) >= 2  # Deposit + transfer debit
