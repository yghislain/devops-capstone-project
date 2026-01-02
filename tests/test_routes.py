"""
Account API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
from unittest import TestCase
from tests.factories import AccountFactory
from service.common import status  # HTTP Status Codes
from service.models import db, Account, init_db
from service import app

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)

BASE_URL = "/accounts"


######################################################################
#  T E S T   C A S E S
######################################################################
class TestAccountService(TestCase):
    """Account Service Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db(app)

    @classmethod
    def tearDownClass(cls):
        """Runs once before test suite"""

    def setUp(self):
        """Runs before each test"""
        db.session.query(Account).delete()  # clean up the last tests
        db.session.commit()

        self.client = app.test_client()

    def tearDown(self):
        """Runs once after each test case"""
        db.session.remove()

    ######################################################################
    #  H E L P E R   M E T H O D S
    ######################################################################

    def _create_accounts(self, count):
        """Factory method to create accounts in bulk"""
        accounts = []
        for _ in range(count):
            account = AccountFactory()
            response = self.client.post(BASE_URL, json=account.serialize())
            self.assertEqual(
                response.status_code,
                status.HTTP_201_CREATED,
                "Could not create test Account",
            )
            new_account = response.get_json()
            account.id = new_account["id"]
            accounts.append(account)
        return accounts

    ######################################################################
    #  A C C O U N T   T E S T   C A S E S
    ######################################################################

    def test_index(self):
        """It should get 200_OK from the Home Page"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_health(self):
        """It should be healthy"""
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "OK")

    def test_create_accounts(self):
        """It should Create a new Account"""
        account = AccountFactory()
        response = self.client.post(
            BASE_URL,
            json=account.serialize(),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_account = response.get_json()
        self.assertEqual(new_account["name"], account.name)
        self.assertEqual(new_account["email"], account.email)
        self.assertEqual(new_account["address"], account.address)
        self.assertEqual(new_account["phone_number"], account.phone_number)
        self.assertEqual(new_account["date_joined"], str(account.date_joined))

    def test_bad_request(self):
        """It should not Create an Account when sending the wrong data"""
        response = self.client.post(BASE_URL, json={"name": "not enough data"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unsupported_media_type(self):
        """It should not Create an Account when sending the wrong media type"""
        account = AccountFactory()
        response = self.client.post(
            BASE_URL,
            json=account.serialize(),
            content_type="test/html"
        )
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_get_account (self):
        """It should read an account based on provided input"""
        account_id = self.test_account.id
        response = self.client.get(f"{BASE_URL}/{account_id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["name"], self.test_account.name)
        self.assertEqual(data["id", account_id])


    def test_list_accounts(self):
        """It should list all the accounts in the service"""
        account1 = AccountFactory()
        account2 = AccountFactory()
        account3 = AccountFactory()
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 3)
    
    def test_update_account(self):
        """It should update an account from the service"""
        test_account = AccountFactory()
        response = self.client.post(
            BASE_URL,
            json=test_account.serialize(),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        created_account  = response.get_json()
        account_id = created_account["id"]

        created_account["name"] = "Updated Name"
        created_account["email"] = "updated@example.com"
    
        # Act - Update the account
        response = self.client.put(
        f"{BASE_URL}/{account_id}",
        json=created_account,
        content_type="application/json"
        )
    
        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
        updated_account = response.get_json()
        self.assertEqual(updated_account["name"], "Updated Name")
        self.assertEqual(updated_account["email"], "updated@example.com")
        self.assertEqual(updated_account["id"], account_id)  # ID shouldn't change
    

    def test_delete_account(self):
        """It should delete the account"""
        # Arrange - Create a test account
        test_account = AccountFactory()
        response = self.client.post(
            BASE_URL,
            json=test_account.serialize(),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        created_account = response.get_json()
        account_id = created_account["id"]
        
        # Act - Delete the account
        response = self.client.delete(f"{BASE_URL}/{account_id}")
        
        # Assert
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)  # No content in response
        
        # Verify account is actually deleted
        get_response = self.client.get(f"{BASE_URL}/{account_id}")
        self.assertEqual(get_response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_account_not_found(self):
        """It should return 404 when getting non-existent account"""
        # Try to get account that doesn't exist
        fake_id = 99999
        response = self.client.get(f"{BASE_URL}/{fake_id}")
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # Verify error message is present
        data = response.get_json()
        self.assertIsNotNone(data)
        self.assertIn("message", data)