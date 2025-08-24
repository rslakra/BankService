import unittest

from fastapi.testclient import TestClient

from config.base import get_settings
from core.database import init_database
from core.logger import getLogger
from main import app

settings = get_settings()

# Create test database
# SQLALCHEMY_DATABASE_URL = settings.SQLALCHEMY_DATABASE_URL
#
# engine = create_engine(
#     SQLALCHEMY_DATABASE_URL,
#     connect_args={"check_same_thread": False},
#     poolclass=StaticPool,
# )
#
# TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base.metadata.create_all(bind=engine)
#
#
# def override_get_db():
#     try:
#         db = TestingSessionLocal()
#         yield db
#     finally:
#         db.close()
#
#
# #
# app.dependency_overrides[get_database()] = override_get_db
init_database()
client = TestClient(app)

logger = getLogger(__name__)


def test_user() -> dict:
    return {
        "email": "test@example.com",
        "password": "testpassword123",
        "full_name": "Test User",
        "phone_number": "+1234567890"
    }


def auth_headers():
    # Create user and get token
    client.post("/signup", json=test_user())
    response = client.post("/login", json={
        "email": test_user()["email"],
        "password": test_user()["password"]
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class BaseTestCase(unittest.TestCase):
    """An AbstractTestCase class"""

    @classmethod
    def setUpClass(cls):
        # set the app at class level
        logger.debug("setUpClass()")
        # cls.app = app
        # cls.client = TestClient(app)
        # cls.app.config.update({
        #     "APP_ENV": AppEnv.TEST.name
        # })

    def setUp(self):
        """The setUp() method of the TestCase class is automatically invoked before each tests"""
        logger.debug("setUp()")
        pass

    def tearDown(self):
        """The tearDown() method of the TestCase class is automatically invoked after each tests"""
        logger.debug("tearDown()")
