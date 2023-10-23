from fastapi.testclient import TestClient
from app import app
import json
from dotenv import load_dotenv
from api.repository.repository import connect
from unittest import TestCase
from api.model.PH_Main.user import User
from fastapi.encoders import jsonable_encoder
from api.model.PH_Community.community_models import CommunityModel
from api.model.PH_Community.announcement_models import AnnouncementModel

load_dotenv()
client = TestClient(app)

db = connect()

class TestAnnouncement(TestCase):
    @classmethod
    def setUpClass(cls):
        # setUpClass: Run once to set up non-modified data for all class methods.
        cls.register = '/api/v1/register'
        cls.login = '/api/v1/login'
        cls.logout = '/api/v1/logout'
        cls.application_encoded = 'application/x-www-form-urlencoded'
        cls.application_json = 'application/json'
        cls.user = User(
            username="test_announcement",
            password="pplasikgaboong",
            name="Admin Community PPL",
            email="test_announcement@ui.ac.id",
            description="Lyfe is never flat as a community admin",
            uiIdentityNumber="1906900222",
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
        cls.profile = db['user'].find_one(
            {'username': 'test_announcement'})
        cls.user2 = User(
            username="test_announcement2",
            password="pplasikgaboong",
            name="Admin Community PPL",
            email="test_announcement2@ui.ac.id",
            description="Lyfe is never flat as a community admin",
            uiIdentityNumber="1906902388",
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
            json=jsonable_encoder(cls.user2)
        )
        cls.profile2 = db['user'].find_one(
            {'username': 'test_announcement2'})

    @classmethod
    def tearDownClass(cls):
        # tearDownClass: Run once to clean up after all class methods has been executed.
        db['user'].delete_one({'username': 'test_announcement'})
        db['user'].delete_one({'username': 'test_announcement2'})

    
    def setUp(self):
       # setUp: Run once for every test method to setup clean data.
        response = client.post(
            self.login,
            headers={
                'Content-Type':self.application_encoded
            },
            data={
                'username': 'test_announcement',
                'password': 'pplasikgaboong',
                'scope': 'me users logout app-admin'
            }
        )
        self.token = response.json()['access_token']
        response2 = client.post(
            self.login,
            headers={
                'Content-Type':self.application_encoded
            },
            data={
                'username': 'test_announcement2',
                'password': 'pplasikgaboong',
                'scope': 'me users logout app-admin'
            }
        )
        self.token2 = response2.json()['access_token']

        # Create Community
        self.community = {
            "name": "TEST_CLUB",
            "admin": "test_announcement@ui.ac.id",
            "shortDescription": "string",
            "longDescription":"string",
            "status": "open",
            "rules": "string",
            "publicMembers": [],
            "pendingMembers": [],
            "totalMembers": 1,
            "tags": [
                "string"
            ],
            "createdAt": "2022-04-04T07:23:21.655070",
            "updatedAt": "2022-04-04T07:23:21.655070"
        }
        self.response_data = client.post(
            "/api/v1/community",
            headers={
                'Authorization': f"Bearer {self.token}"
            },
            data = {
                "community": json.dumps(self.community)
            }
        )
        self.community_id= self.response_data.json()['_id']

        # Create announcement
        self.announcement = AnnouncementModel(
            content= "TEST",
            communityId= self.community_id,
        )
        self.data_announcement = jsonable_encoder(self.announcement)
        client.post(
            f"/api/v1/announcement/{self.community_id}",
            json=jsonable_encoder(self.announcement),
            headers={
                'accept': self.application_json,
                'Authorization': f"Bearer {self.token}"
            }
        )
        self.announcement_id = jsonable_encoder(self.announcement)['_id']
        # Create announcement2
        self.announcement2 = AnnouncementModel(
            content= "TEST",
            communityId= 123456,
        )
        self.data_announcement2 = jsonable_encoder(self.announcement2)
        client.post(
            f"/api/v1/announcement/123456",
            json=jsonable_encoder(self.announcement2),
            headers={
                'accept': self.application_json,
                'Authorization': f"Bearer {self.token}"
            }
        )
        self.announcement_id2 = jsonable_encoder(self.announcement2)['_id']


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
        db['announcement'].delete_many({"content": "TEST"})
        db['announcement'].delete_many({"content": "TEST_edit"})
        db['communities'].delete_many({'name':'TEST_CLUB'})


    def test_create_announcement_valid(self):
        response = client.post(
            "api/v1/announcement/6969",
            json={
                "content":"TEST"
            },
            headers={
                'accept': self.application_json,
                'Authorization': f"Bearer {self.token}"
            }
        )
        assert response.status_code == 201
        assert response.json()['content'] == "TEST"
    
    def test_get_announcement_from_community_id_invalid(self):
        response = client.get(
            f"/api/v1/announcement/202020/community",
            headers={
            'accept': self.application_json,
            'Authorization': f"Bearer {self.token}"
            }
        )
        assert response.status_code == 404
        assert response.json()['detail'] == "community 202020 not found"
    
    def test_get_announcement_from_community_id_valid(self):
        response = client.get(
            f"api/v1/announcement/{self.community_id}/community",
            headers={
                'accept': self.application_json,
                'Authorization': f"Bearer {self.token}"
            }

        )
        assert response.status_code == 200
        assert response.json()[0]['content'] == "TEST"

    
    def test_get_all_announcement(self):
        response = client.get(
            "/api/v1/announcement",
            headers={
            'accept': self.application_json,
            'Authorization': f"Bearer {self.token}"
            }
        )
        assert response.status_code == 200
        assert self.data_announcement['content'] in response.json()[-1]['content']

    def test_update_announcement_not_found(self):
        response = client.put(
            "/api/v1/announcement/200",
            json={
                "content":"TEST_edit"
            },
            headers={
            'accept': self.application_json,
            'Authorization': f"Bearer {self.token}"
            }
        )
        assert response.status_code == 404
        assert response.json()['detail'] == 'announcement 200 not found'
    
    def test_update_valid(self):
        response = client.put(
            f"/api/v1/announcement/{self.announcement_id}",
            json={
                "content":"TEST_edit"
            },
            headers={
            'accept': self.application_json,
            'Authorization': f"Bearer {self.token}"
            }
        )
        assert response.status_code == 200
        assert response.json()['content'] == "TEST_edit"
    
    def test_update_not_admin(self):
        response = client.put(
            f"/api/v1/announcement/{self.announcement_id}",
            json={
                "content":"TEST_edit"
            },
            headers={
            'accept': self.application_json,
            'Authorization': f"Bearer {self.token2}"
            }
        )
        assert response.status_code == 401
        assert response.json()['detail'] == "You're not admin of TEST_CLUB"
    
    def test_update_but_community_not_found(self):
        response = client.put(
            f"/api/v1/announcement/{self.announcement_id2}",
            json={
                "content":"TEST_edit"
            },
            headers={
            'accept': self.application_json,
            'Authorization': f"Bearer {self.token2}"
            }
        )
        assert response.status_code == 404
        assert response.json()['detail']== "community 123456 not found"

    def test_delete_announcement_not_found(self):
        response = client.delete(
            f"api/v1/announcement/6969",
            headers={
                'accept': self.application_json,
                'Authorization': f"Bearer {self.token}"
            }
        )
        assert response.status_code == 404
        assert response.json()['detail'] == 'announcement 6969 not found'
    
    def test_delete_success(self):
        response = client.delete(
            f"api/v1/announcement/{self.announcement_id}",
            headers={
                'accept': self.application_json,
                'Authorization': f"Bearer {self.token}"
            }
        )
        assert response.status_code == 204
        assert response.json()['detail'] == f'announcement {self.announcement_id} has been deleted'
    
    def test_delete_but_community_not_found(self):
        response = client.delete(
            f"api/v1/announcement/{self.announcement_id2}",
            headers={
                'accept': self.application_json,
                'Authorization': f"Bearer {self.token2}"
            }
        )
        assert response.status_code == 404
        assert response.json()['detail'] == "community 123456 not found"
    
    def test_delete_not_an_admin(self):
        response = client.delete(
            f"api/v1/announcement/{self.announcement_id}",
            headers={
                'accept': self.application_json,
                'Authorization': f"Bearer {self.token2}"
            }
        )
        assert response.status_code == 401
        assert response.json()['detail'] == "You're not admin of TEST_CLUB"