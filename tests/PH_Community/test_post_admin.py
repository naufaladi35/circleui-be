import json
from fastapi import status
from unittest import TestCase
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from fastapi.encoders import jsonable_encoder

from app import app
from api.model.PH_Main.user import User
from api.model.PH_Community.post import Post
from api.model.PH_Community.community_models import CommunityModel
from api.repository.repository import connect

load_dotenv()
client = TestClient(app)

db = connect()

class TestPost(TestCase):
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
            username = "admin_maudelete",
            password = "pplasikgaboong",
            name = "Admin Delete",
            email = "admindelete@ui.ac.id",
            description = "hapus",
            uiIdentityNumber = "190641231414",
            faculty = "faculty of Psychology",
            classOf = "2010",
            linkedin = "linkedin.com/admin_delete",
            twitter = "twitter.com/admin_delete",
            instagram = "instagram.com/admin_delete",
            tiktok = "tiktok.com/admin_delete",
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
        cls.profile = db['user'].find_one({ 'username': 'admin_maudelete' })
    
    @classmethod
    def tearDownClass(cls):
        # tearDownClass: Run once to clean up after all class methods has been executed.
        db['user'].delete_one({ 'username': 'admin_maudelete' })
    
    def setUp(self):
        # setUp: Run once for every test method to setup clean data.
        response = client.post(
            self.login,
            headers = {
                'Content-Type': self.application_encoded
            },
            data = {
                'username': 'admin_maudelete',
                'password': 'pplasikgaboong',
                'scope': self.scopes
            }
        )
        self.token = response.json()['access_token']

        self.community = {
            "name": "AntiDeleteDeleteClub",
            "admin": "admindelete@ui.ac.id",
            "shortDescription": "keren",
            "longDescription": "keren pake banget",
            "status": "open",
            "rules": "Jangan berisik!!!!",
            "pendingMembers": []
        }
        self.response_community_data = client.post(
            "/api/v1/community",
            headers={
                'accept': self.application_json,
                'Authorization': f"Bearer {self.token}"
            },
            data = {
                "community": json.dumps(self.community)
            }
        )
        print(self.response_community_data.json())
        self.community_id = self.response_community_data.json()['_id']
        self.post_data = {
            "title": "Postingan ini bakal di delete",
            "content": "Hapus aku",
            "communityId": self.community_id,
            "userLiked": []
        }
        self.response_post_data = client.post(
            url = '/api/v1/post',
            headers = {
                'Authorization': f"Bearer {self.token}"
            },
            data = {
                "form_data": json.dumps(self.post_data)
            },
        )
        self.response_id = self.response_post_data.json()['inserted_id']

    def tearDown(self):
        # tearDown: Clean up run after every test method.
        client.get(
            url = self.logout,
            headers = {
                'accept': self.application_json,
                'Authorization': f"Bearer {self.token}"
            }
        )
        db['post'].delete_one({"_id": self.response_id })
        db['communities'].delete_many({"name": "AntiDeleteDeleteClub"})

    def test_admin_delete_post_valid(self):
        response = client.delete(
            url = f"/api/v1/post/{self.response_id}/admin-delete",
            headers = {
                'accept': self.application_json,
                'Authorization': f"Bearer {self.token}"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()['status'] == 'deleted by admin'
        assert response.json()['acknowledged'] == True
        assert response.json()['deleted_count'] == 1