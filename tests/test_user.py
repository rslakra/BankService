from tests.base import client, BaseTestCase, test_user, auth_headers


class TestUser(BaseTestCase):

    def test_signup_success(self):
        data_json = test_user()
        response = client.post("/signup", json=data_json)
        data = response.json()
        if response.status_code == 400:
            assert data["detail"] == "Email already registered"
        elif response.status_code == 200:
            assert response.status_code == 200
            assert data["email"] == data_json["email"]
            assert data["full_name"] == data_json["full_name"]
            assert "id" in data

    def test_signup_duplicate_email(self):
        client.post("/signup", json=test_user())
        response = client.post("/signup", json=test_user())
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]

    def test_signup_invalid_password(self):
        data_json = test_user()
        data_json["password"] = "123"  # Too short
        response = client.post("/signup", json=data_json)
        assert response.status_code == 422

    def test_login_success(self):
        client.post("/login", json=test_user())
        response = client.post("/login", json={
            "email": test_user()["email"],
            "password": test_user()["password"]
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_credentials(self):
        response = client.post("/login", json={
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        })
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]

    def test_get_current_user(self):
        response = client.get("/me", headers=auth_headers())
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user()["email"]
        # assert data["full_name"] == test_user()["full_name"]

        # def test_update_current_user(self):
        update_data = {
            "full_name": "Updated Name",
            "phone_number": "+19876543210"
        }
        response = client.put("/me", json=update_data, headers=auth_headers())
        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == update_data["full_name"]
        assert data["phone_number"] == update_data["phone_number"]

    def test_unauthorized_access(self):
        response = client.get("/me")
        assert response.status_code == 403
