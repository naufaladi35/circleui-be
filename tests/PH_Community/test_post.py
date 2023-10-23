import os, json
from fastapi import status
from unittest import TestCase
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from fastapi.encoders import jsonable_encoder

from app import app
from api.model.PH_Main.user import User
from api.model.PH_Community.post import Post
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
        cls.multipart_form_data = 'multipart/form-data'
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

        self.post_data = {
            "title": "Postingan Valid",
            "content": "Content didalam postingan yang valid",
            "communityId": 1,
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
            files = {
                "file": ('bentley.jpg', open('assets/bentley.jpg', 'rb'), 'image/jpeg')
            }
        )
        self.response_id = self.response_post_data.json()['inserted_id']
  
    def tearDown(self):
        # tearDown: Clean up run after every test method.
        db['post'].delete_many({'communityId':'1'})
    
    def test_get_community_posts_valid(self):
        response = client.get(
            url = '/api/v1/posts/1',
            headers = {
                'accept': self.application_json,
                'Authorization': f"Bearer {self.token}"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()['accessed_by'] == 'admin_budackPPL'
        assert len(response.json()['content']) == 1
    
    def test_get_community_post_invalid_permission(self):
        response = client.get(
            url = '/api/v1/posts/a'
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_specific_post_valid(self):
        response = client.get(
            url = f'/api/v1/post/{self.response_id}',
            headers = {
                'accept': self.application_json,
                'Authorization': f"Bearer {self.token}"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()['accessed_by'] == 'admin_budackPPL'
        assert response.json()['content']['_id'] == self.response_id
    
    def test_get_specific_post_invalid_permission(self):
        response = client.get(
            url = '/api/v1/post/1'
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_create_post_valid(self):
        response = self.response_post_data
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()['status'] == 'accepted'
        assert response.json()['acknowledged'] == True

        db['post'].delete_one({ '_id': response.json()['inserted_id'] })
    
    def test_create_post_invalid_permission(self):
        response = client.post(
            url = '/api/v1/post',
            json = jsonable_encoder(self.post_data),
            headers = {
                'accept': self.application_json
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_create_post_invalid_file_attachment(self):
        response = client.post(
            url = '/api/v1/post',
            headers = {
                'Authorization': f"Bearer {self.token}"
            },
            data = {
                "form_data": json.dumps(self.post_data)
            },
            files = {
                "file": ('test.txt', open('assets/test.txt', 'rb'), 'text/plain')
            }
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == 'File type not allowed'
    
    def test_post_toggle_like_valid(self):
        response_toggle = client.post(
            url = f"/api/v1/post/{self.response_id}/toggle-like",
            headers = {
                'accept': self.application_json,
                'Authorization': f"Bearer {self.token}"
            }
        )
        assert response_toggle.status_code == status.HTTP_200_OK
        assert response_toggle.json()['message'] == 'liked'
    
    def test_post_toggle_unlike_valid(self):
        client.post(
            url = f'/api/v1/post/{self.response_id}/toggle-like',
            headers = {
                'accept': self.application_json,
                'Authorization': f"Bearer {self.token}"
            }
        )

        response_toggle = client.post(
            url = f'/api/v1/post/{self.response_id}/toggle-like',
            headers = {
                'accept': self.application_json,
                'Authorization': f"Bearer {self.token}"
            }
        )
        assert response_toggle.status_code == status.HTTP_200_OK
        assert response_toggle.json()['message'] == 'unliked'
    
    def test_post_toggle_like_invalid_id(self):
        response = client.post(
            url = '/api/v1/post/1/toggle-like',
            headers = {
                'accept': self.application_json,
                'Authorization': f"Bearer {self.token}"
            }
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()['status'] == 'not found'
        assert response.json()['message'] == 'post is not found'
    
    def test_update_post_valid(self):
        update_post = Post(
            _id = self.response_id,
            title = "Postingan untuk update gan",
            content = "Content sebagai update",
            communityId = 1,
            userLiked = []
        )
        response = client.put(
            url = f'/api/v1/post/{self.response_id}',
            json = jsonable_encoder(update_post),
            headers = {
                'accept': self.application_json,
                'Authorization': f"Bearer {self.token}"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()['status'] == 'updated'
        assert response.json()['message'] == 'your post is successfully updated'

        db['post'].delete_one({ '_id': self.response_id })
    
    def test_update_post_different_creator_and_updater_valid(self):
        update_post = Post(
            _id = self.response_id,
            title = "Postingan untuk update gan",
            content = "Content sebagai update",
            communityId = 1,
            creator = "digantiakunbaru@ui.ac.id",
            userLiked = []
        )
        client.put(
            url = f'/api/v1/post/{self.response_id}',
            json = jsonable_encoder(update_post),
            headers = {
                'accept': self.application_json,
                'Authorization': f"Bearer {self.token}"
            }
        )

        response = client.put(
            url = f'/api/v1/post/{self.response_id}',
            json = jsonable_encoder(update_post),
            headers = {
                'accept': self.application_json,
                'Authorization': f"Bearer {self.token}"
            }
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json()['status'] == 'prohibited'
        assert response.json()['message'] == 'you are not the creator of this post'

        db['post'].delete_one({ '_id': self.response_id })
    
    def test_update_post_invalid_post_id(self):
        response = client.put(
            url = '/api/v1/post/1',
            json = jsonable_encoder(self.post_data),
            headers = {
                'accept': self.application_json,
                'Authorization': f"Bearer {self.token}"
            }
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()['status'] == 'not found'
        assert response.json()['message'] == 'post is not found'
    
    def test_delete_post_valid(self):
        response = client.delete(
            url = f"/api/v1/post/{self.response_id}",
            headers = {
                'accept': self.application_json,
                'Authorization': f"Bearer {self.token}"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()['status'] == 'deleted'
        assert response.json()['acknowledged'] == True
        assert response.json()['deleted_count'] == 1
    
    def test_delete_post_different_creator_and_deleter_valid(self):
        update_post = Post(
            _id = self.response_id,
            title = "Postingan untuk delete gan",
            content = "Content sebagai delete different creator and deleter",
            communityId = 1,
            creator = "digantiakunbaru@ui.ac.id",
            userLiked = []
        )
        client.put(
            url = f'/api/v1/post/{self.response_id}',
            json = jsonable_encoder(update_post),
            headers = {
                'accept': self.application_json,
                'Authorization': f"Bearer {self.token}"
            }
        )

        response = client.delete(
            url = f'/api/v1/post/{self.response_id}',
            headers = {
                'accept': self.application_json,
                'Authorization': f"Bearer {self.token}"
            }
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json()['status'] == 'forbidden'
        assert response.json()['message'] == 'you are not the creator of this post'

        db['post'].delete_one({ '_id': self.response_id })

    def test_delete_post_invalid_id(self):
        response = client.delete(
            url = f"/api/v1/post/1",
            headers = {
                'accept': self.application_json,
                'Authorization': f"Bearer {self.token}"
            }
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()['status'] == 'not found'
        assert response.json()['message'] == 'post is not found'
