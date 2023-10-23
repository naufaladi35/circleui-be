from fastapi.testclient import TestClient
from app import app
import json
from dotenv import load_dotenv
from api.repository.repository import connect
from unittest import TestCase
from api.model.PH_Main.user import User
from fastapi.encoders import jsonable_encoder
from api.model.PH_Community.community_models import CommunityModel
from api.model.PH_Community.post import Post
from api.model.PH_Community.comment_models import *

load_dotenv()
client = TestClient(app)

db = connect()

class TestComment(TestCase):
    @classmethod
    def setUpClass(cls):
        # setUpClass: Run once to set up non-modified data for all class methods.
        cls.register = '/api/v1/register'
        cls.login = '/api/v1/login'
        cls.logout = '/api/v1/logout'
        cls.application_encoded = 'application/x-www-form-urlencoded'
        cls.application_json = 'application/json'
        cls.user = User(
            username="test_comment",
            password="pplasikgaboong",
            name="Admin Community PPL",
            email="test_comment@ui.ac.id",
            description="Lyfe is never flat as a community admin",
            uiIdentityNumber="1906900999",
            faculty="faculty of Psychology",
            classOf="2010",
            linkedin="linkedin.com/admin_budackPPL",
            twitter="twitter.com/admin_budackPPL",
            instagram="instagram.com/admin_budackPPL",
            tiktok="tiktok.com/admin_budackPPL",
            communityEnrolled=[
                "string"
            ],
            eventEnrolled=[
                "string"
            ]
        )
        cls.user2 = User(
            username="test_comment2",
            password="pplasikgaboong",
            name="Admin Community PPL",
            email="test_comment2@ui.ac.id",
            description="Lyfe is never flat as a community admin",
            uiIdentityNumber="1906900998",
            faculty="faculty of Psychology",
            classOf="2010",
            linkedin="linkedin.com/admin_budackPPL",
            twitter="twitter.com/admin_budackPPL",
            instagram="instagram.com/admin_budackPPL",
            tiktok="tiktok.com/admin_budackPPL",
            communityEnrolled=[
                "string"
            ],
            eventEnrolled=[
                "string"
            ]
        )
        client.post(
            url=cls.register,
            json=jsonable_encoder(cls.user)
        )
        client.post(
            url=cls.register,
            json=jsonable_encoder(cls.user2)
        )
        cls.profile = db['user'].find_one(
            {'username': 'test_comment'})
        cls.profile2 = db['user'].find_one(
            {'username': 'test_comment2'})
    
    @classmethod
    def tearDownClass(cls):
        # tearDownClass: Run once to clean up after all class methods has been executed.
        db['user'].delete_one({'username': 'test_comment'})


    def setUp(self):
        # setUp: Run once for every test method to setup clean data.
        response = client.post(
            self.login,
            headers={
                'Content-Type':self.application_encoded
            },
            data={
                'username': 'test_comment',
                'password': 'pplasikgaboong',
                'scope': 'me users logout app-admin'
            }
        )
        self.token = response.json()['access_token']
        response2 = client.post(
            self.login,
            headers={
                'Content-Type': self.application_encoded
            },
            data={
                'username': 'test_comment2',
                'password': 'pplasikgaboong',
                'scope': 'me users logout app-admin'
            }
        )
        self.token2 = response2.json()['access_token']
        # Create Community
        self.community = CommunityModel(
            name= "Volleyball",
            admin= "test_comment@ui.ac.id",
            shortDescription= "string",
            longDescription= "string",
            status= "open",
            rules= "string",
            publicMembers= [],
            pendingMembers= [],
            totalMembers= 1,
            tags= [
                "string"
            ],
            createdAt= "2022-04-04T07:23:21.655070",
            updatedAt= "2022-04-04T07:23:21.655070"
        )
        client.post(
            "/api/v1/community",
            json=jsonable_encoder(self.community),
            headers={
                'accept': self.application_json,
                'Authorization': f"Bearer {self.token}"
            }
        )
        # Create Post
        self.post = {
            "title": "string",
            "content": "string",
            "communityId": jsonable_encoder(self.community)['_id'],
            "userLiked": []
        }
        self.response_post_data = client.post(
            "/api/v1/post",
            headers={
                'Authorization': f"Bearer {self.token}"
            },
            data = {
                "form_data": json.dumps(self.post)
            }
        )
        self.response_id = self.response_post_data.json()['inserted_id']
        
        # Create Comment
        self.comment =  CommentModel(
            content= "TEST",
        )
        self.comment2 = CommentModel(
            content="KARASUNO",
            creator= "test_comment@ui.ac.id",
            postId= self.response_id

        )
        self.comment3 = CommentModel(
            content="KARASUNO 2",
            creator= "test_comment2@ui.ac.id",
            postId= self.response_id

        )
        self.data1 = jsonable_encoder(self.comment)
        client.post(
            f"/api/v1/comment/{self.response_id}",
            json=jsonable_encoder(self.comment2),
            headers={
                'accept': self.application_json,
                'Authorization': f"Bearer {self.token}"
            }
        )
        client.post(
            f"/api/v1/comment/{self.response_id}",
            json=jsonable_encoder(self.comment3),
            headers={
                'accept': self.application_json,
                'Authorization': f"Bearer {self.token2}"
            }
        )
        client.post(
            "/api/v1/comment/6969",
            json=jsonable_encoder(self.comment),
            headers={
            'accept': self.application_json,
            'Authorization': f"Bearer {self.token}"
            }
        )

    def tearDown(self):
        # tearDown: Clean up run after every test method.
        client.get(
            url=self.logout,
            headers={
                'accept': self.application_json,
                'Authorization': f"Bearer {self.token}"
            }
        )
        client.get(
            url=self.logout,
            headers={
                'accept': self.application_json,
                'Authorization': f"Bearer {self.token2}"
            }
        )
        db['comment'].delete_many({"email": "test_comment@ui.ac.id"})
        db['comment'].delete_many({"email": "test_comment2@ui.ac.id"})

    def test_create_comment_invalid(self):
        response = client.post(
            "/api/v1/comment/6969",
            json={
                
            },
            headers={
                'accept': self.application_json,
                'Authorization': f"Bearer {self.token}"
            }
        )
        assert response.status_code == 422
        assert response.json() == {
            "detail": [
                {
                    "loc": [
                        "body",
                        "content"
                    ],
                    "msg": "field required",
                    "type": "value_error.missing"
                }
            ]
        }

    def test_create_comment_valid(self):
        response = client.post(
            "/api/v1/comment/6969",
            json={
                "content":"TEST"
            },
            headers={
                'accept': self.application_json,
                'Authorization': f"Bearer {self.token}"
            }
        )
        assert response.status_code == 201
        assert response.json()['email'] == "test_comment@ui.ac.id"

    def test_get_comment_from_post_id_invalid(self):
        response = client.get(
            f"/api/v1/comment/202020/post",
            headers={
            'accept': self.application_json,
            'Authorization': f"Bearer {self.token}"
            }
        )
        assert response.status_code == 404
        assert response.json()['detail'] == "Post 202020 not found"

    def test_get_comment_from_post_id_valid(self):
        response = client.get(
            f"/api/v1/comment/6969/post",
            headers={
            'accept': self.application_json,
            'Authorization': f"Bearer {self.token}"
            }
        )
        assert response.status_code == 200
        assert response.json()[0]['postId'] == "6969"

    def test_get_comment(self):
        response = client.get(
            "/api/v1/comment",
            headers={
            'accept': self.application_json,
            'Authorization': f"Bearer {self.token}"
            }
        )
        assert response.status_code == 200
        assert self.data1['content'] in response.json()[-1]['content']

    def test_delete_comment_invalid(self):
        response = client.delete(
            f"/api/v1/comment/1233",
            headers={
                'accept': self.application_json,
                'Authorization': f"Bearer {self.token}"
            }
        )
        assert response.status_code == 404
        assert response.json()['detail'] == "comment 1233 not found"

    def test_delete_comment_valid(self):
        response = client.delete(
            f"/api/v1/comment/{jsonable_encoder(self.comment2)['_id']}",
            headers={
                'accept': self.application_json,
                'Authorization': f"Bearer {self.token}"
            }
        )
        assert response.status_code == 204

    def test_update_comment_valid(self):
        response = client.put(
            f"api/v1/comment/{jsonable_encoder(self.comment)['_id']}",
            json={
                "content": "Sumpah Faris keren banget"
            },
            headers={
                'accept': self.application_json,
                'Authorization': f"Bearer {self.token}"
            }
        )
        assert response.status_code == 200
        assert response.json()['content'] == "Sumpah Faris keren banget"

    def test_update_comment_invalid_id(self):
        response = client.put(
            f"api/v1/comment/idinigakada",
            json={
                "content": "Sumpah Faris keren banget"
            },
            headers={
                'accept': self.application_json,
                'Authorization': f"Bearer {self.token}"
            }
        )
        assert response.status_code == 404

    def test_update_comment_invalid_user(self):
        client.get(
            url=self.logout,
            headers={
                'accept': self.application_json,
                'Authorization': f"Bearer {self.token}"
            }
        )
        response2 = client.post(
            self.login,
            headers={
                'Content-Type': self.application_encoded
            },
            data={
                'username': 'test_comment2',
                'password': 'pplasikgaboong',
                'scope': 'me users logout app-admin'
            }
        )
        self.token2 = response2.json()['access_token']
        response = client.put(
            f"api/v1/comment/{jsonable_encoder(self.comment)['_id']}",
            json={
                "content": "Sumpah Faris keren banget"
            },
            headers={
                'accept': self.application_json,
                'Authorization': f"Bearer {self.token2}"
            }
        )
        assert response.status_code == 401