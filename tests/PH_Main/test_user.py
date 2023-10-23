from fastapi import status
from unittest import TestCase
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from fastapi.encoders import jsonable_encoder

from app import app
from api.model.PH_Main.user import User, updateUser
from api.repository.repository import connect
import json

load_dotenv()
client = TestClient(app)

db = connect()

class TestUser(TestCase):
    @classmethod
    def setUpClass(cls):
        # setUpClass: Run once to set up non-modified data for all class methods.
        cls.register = '/api/v1/register'
        cls.login = '/api/v1/login'
        cls.logout = '/api/v1/logout'
        cls.application_encoded = 'application/x-www-form-urlencoded'
        cls.application_json = 'application/json'
        cls.scopes = 'me users logout'
        cls.error_detail = 'Could not validate credentials'

        cls.user = User(
            username = "admin_budackPPL",
            password = "pplasikgaboong",
            name = "Admin Budack PPL",
            email = "adminbudackPPL@ui.ac.id",
            description = "Lyfe is never flat as an admin",
            uiIdentityNumber = "1906736290",
            faculty = "faculty of Psychology",
            classOf = "2010",
            linkedin = "linkedin.com/admin_budackPPL",
            twitter = "twitter.com/admin_budackPPL",
            instagram = "instagram.com/admin_budackPPL",
            tiktok = "tiktok.com/admin_budackPPL",
            communityEnrolled = [
                "string"
            ],
            eventEnrolled = [
                "string"
            ]
        )
        client.post(
            url = cls.register,
            json = jsonable_encoder(cls.user)
        )
        cls.profile = db['user'].find_one({ 'username': 'admin_budackPPL' })


    @classmethod
    def tearDownClass(cls):
        # tearDownClass: Run once to clean up after all class methods has been executed.
        db['user'].delete_one({ 'username': 'admin_budackPPL' })

    def setUp(self):
        # setUp: Run once for every test method to setup clean data.
        response = client.post(
            self.login,
            headers = {
                'Content-Type': self.application_encoded
            },
            data = {
                'username': 'admin_budackPPL',
                'password': 'pplasikgaboong',
                'scope': self.scopes
            }
        )
        self.token = response.json()['access_token']
  
    def tearDown(self):
        # tearDown: Clean up run after every test method.
        client.get(
            url = self.logout,
            headers = {
                'accept': self.application_json,
                'Authorization': f"Bearer {self.token}"
            }
        )

    def test_user_register_valid(self):
        user = User(
            username = "budackPPL",
            password = "pplasikgaboong",
            name = "Budack PPL",
            email = "budackPPL@ui.ac.id",
            description = "Lyfe is never flat",
            uiIdentityNumber = "1906678463",
            faculty = "faculty of law",
            classOf = "2010",
            linkedin = "linkedin.com/budackPPL",
            twitter = "twitter.com/budackPPL",
            instagram = "instagram.com/budackPPL",
            tiktok = "tiktok.com/budackPPL",
            communityEnrolled = [
            "string"
            ],
            eventEnrolled = [
            "string"
            ]
        )
        response = client.post(
            url = self.register,
            json = jsonable_encoder(user)
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()['status'] == 'accepted'

        db['user'].delete_one({ 'username': 'budackPPL' })
  
    def test_user_register_email_invalid(self):
        user = User(
            username = "invalidEmail_budackPPL",
            password = "pplasikgaboong",
            name = "Budack PPL",
            email = "budackPPL@ui.acc.id",
            description = "Just do it",
            uiIdentityNumber = "123123",
            faculty = "faculty of invalid email",
            classOf = "2010",
            linkedin = "linkedin.com/invalidEmail_budackPPL",
            twitter = "twitter.com/invalidEmail_budackPPL",
            instagram = "instagram.com/invalidEmail_budackPPL",
            tiktok = "tiktok.com/invalidEmail_budackPPL",
            communityEnrolled = [
            "string"
            ],
            eventEnrolled = [
            "string"
            ]
        )
        response = client.post(
            url = self.register,
            json = jsonable_encoder(user)
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {
            'message': 'This is not valid UI email', 
            'status': 'rejected'
        }
    
    def test_user_register_NPM_invalid(self):
        user = User(
            username = "invalidNPM_budackPPL",
            password = "pplasikgaboong",
            name = "Budack PPL",
            email = "budackPPL@ui.ac.id",
            description = "Say the magic word!",
            uiIdentityNumber = "1906736290",
            faculty = "faculty of invalid NPM",
            classOf = "2010",
            linkedin = "linkedin.com/invalidNPM_budackPPL",
            twitter = "twitter.com/invalidNPM_budackPPL",
            instagram = "instagram.com/invalidNPM_budackPPL",
            tiktok = "tiktok.com/invalidNPM_budackPPL",
            communityEnrolled = [
            "string"
            ],
            eventEnrolled = [
            "string"
            ]
        )
        response = client.post(
            url = self.register,
            json = jsonable_encoder(user)
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {
            'status': 'rejected',
            'message': f"either username {user.username} or email {user.email} or NPM {user.uiIdentityNumber} is exist. Please check again!"
        }
    
    def test_user_read_me_valid(self):
        response = client.get(
            url = '/api/v1/users/me',
            headers = {
                'accept': self.application_json,
                'Authorization': f"Bearer {self.token}"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()['user']['_id'] == jsonable_encoder(self.user)['_id']
    
    def test_user_read_me_invalid(self):
        response = client.get(
            url = '/api/v1/users/me',
            headers = {
                'accept': self.application_json,
                'Authorization': f"Bearer "
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {
            'detail': self.error_detail
        }
    
    def test_user_read_other_users_valid(self):
        response = client.get(
            url = '/api/v1/users',
            headers = {
                'accept': self.application_json,
                'Authorization': f"Bearer {self.token}"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()['accessed_by'] == 'admin_budackPPL'

    def test_user_read_other_users_invalid(self):
        response = client.get(
            url = '/api/v1/users',
            headers = {
                'accept': self.application_json,
                'Authorization': f"Bearer "
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {
            'detail': self.error_detail
        }
    
    def test_user_login_username_doesnt_exist_invalid(self):
        response = client.post(
            self.login,
            headers = {
                'Content-Type': self.application_encoded
            },
            data = {
                'username': 'admin_budackPPLLL',
                'password': 'pplasikgaboong',
                'scope': self.scopes
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {
            'detail': "Incorrect username, admin_budackPPLLL is not exist"
        }
    
    def test_user_login_password_invalid(self):
        response = client.post(
            self.login,
            headers = {
                'Content-Type': self.application_encoded
            },
            data = {
                'username': 'admin_budackPPL',
                'password': 'pplasikgabooong',
                'scope': self.scopes
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {
            'detail': "Incorrect password, pplasikgabooong did not match with admin_budackPPL"
        }
  
    def test_user_logout_valid(self):
        response = client.get(
            url = self.logout,
            headers = {
                'accept': self.application_json,
                'Authorization': f"Bearer {self.token}"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            'access_token': False,
            'token_type': None,
            'status': True
        }
  
    def test_user_logout_invalid(self):
        response = client.get(
            url = self.logout,
            headers = {
                'accept': self.application_json,
                'Authorization': f"Bearer "
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {
            'detail': self.error_detail
        }
    
    def test_user_update_valid(self):
        user = {
            "name" : "Budack PPL kuy",
            "description" : "Lyfe is never curve",
            "faculty" : "faculty of law",
            "classOf" : "2010",
            "linkedin" : "linkedin.com/budackPPL",
            "twitter" : "twitter.com/budackPPL",
            "instagram" : "instagram.com/budackPPL",
            "tiktok" : "tiktok.com/budackPPL",
            "updatedAt" : "2022-03-07T04:18:57.012Z"
        }
        response = client.put(
            url = '/api/v1/users/me/update',
            headers = {
                'Authorization': f"Bearer {self.token}"
            },
            data = {
                'form_data': json.dumps(user)
            }
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
        'status': 'accepted',
        'message': 'Update profile successful'
        }

    def test_user_update_invalid(self):
        user = updateUser(
            name = "Budack PPL kuy",
            description = "Lyfe is never curve",
            faculty = "faculty of law",
            classOf = "2010",
            linkedin = "linkedin.com/budackPPL",
            twitter = "twitter.com/budackPPL",
            instagram = "instagram.com/budackPPL",
            tiktok = "tiktok.com/budackPPL",
            updatedAt = "2022-03-07T04:18:57.012Z"
        )
        response = client.put(
            url = '/api/v1/users/me/update',
            json = jsonable_encoder(user),
            headers = {
                'accept': 'application/json',
                'Authorization': f"Bearer "
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_user_by_email(self):
        response = client.get(
            url = '/api/v1/users/adminbudackPPL@ui.ac.id',
            headers = {
                'Authorization': f"Bearer {self.token}"
            },
        )
        assert response.json()['username'] == "admin_budackPPL"