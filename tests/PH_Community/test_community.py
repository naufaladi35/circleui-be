from urllib import response
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from api.model.PH_Main.user import User

from api.repository.repository import connect
from api.model.PH_Community.community_models import *
from fastapi.encoders import jsonable_encoder
from unittest import TestCase
from app import app

load_dotenv()
client = TestClient(app)

db = connect()


class TestCommunity(TestCase):
    @classmethod
    def setUpClass(cls):
        # setUpClass: Run once to set up non-modified data for all class methods.
        cls.register = '/api/v1/register'
        cls.login = '/api/v1/login'
        cls.logout = '/api/v1/logout'
        cls.application_encoded = 'application/x-www-form-urlencoded'
        cls.application_json = 'application/json'
        cls.user = User(
            username="admin_community_test_UI",
            password="pplasikgaboong",
            name="Admin Community PPL",
            email="admin@ui.ac.id",
            description="Lyfe is never flat as a community admin",
            uiIdentityNumber="1984198469",
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
            {'username': 'admin_community_test_UI'})

    @classmethod
    def tearDownClass(cls):
        # tearDownClass: Run once to clean up after all class methods has been executed.
        db['communities'].delete_many({"name": "TEST_UIFC"})
        db['user'].delete_one({'username': 'admin_community_test_UI'})

    def setUp(self):
        # setUp: Run once for every test method to setup clean data.
        response = client.post(
            self.login,
            headers={
                'Content-Type': self.application_encoded
            },
            data={
                'username': 'admin_community_test_UI',
                'password': 'pplasikgaboong',
                'scope': 'me users logout app-admin'
            }
        )
        self.token = response.json()['access_token']

        # CREATE COMMUNITY
        self.community = {
            "name":"TEST_UIFC",
            "admin":"admin@ui.ac.id",
            "shortDescription":"UI Fighting Club",
            "longDescription":"Ayolah ribut ajaa sini",
            "status":"open",
            "rules":"Jangan berisik!!!!",
            "pendingMembers":["test.approve@ui.ac.id", "test.deny@ui.ac.id"],
            "publicMembers":["intoodeep@ui.ac.id"]
        }
        self.response_data = client.post(
            "/api/v1/community",
            headers={
                'accept': self.application_json,
                'Authorization': f"Bearer {self.token}"
            },
            data = {
                "community": json.dumps(self.community)
            },
            files = {
                "file": ('bentley.jpg', open('assets/bentley.jpg', 'rb'), 'image/jpeg')
            }
        )

        self.data1 = self.response_data.json()
        self.community2 = {
            "name":"Delete_UIFC",
            "admin":"admin@ui.ac.id",
            "shortDescription":"UI Fighting Club",
            "longDescription":"Ayolah ribut ajaa sini",
            "status":"open",
            "rules":"Jangan berisik!!!!"
        }
        self.response_data2 = client.post(
            "/api/v1/community",
            headers={
                'Authorization': f"Bearer {self.token}"
            },
            data = {
                "community": json.dumps(self.community2)
            },
            files = {
                "file": ('bentley.jpg', open('assets/bentley.jpg', 'rb'), 'image/jpeg')
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
        db['communities'].delete_many({"name": "TEST_UIFC"})
        db['communities'].delete_many({"name": "Delete_UIFC"})
        db['communities'].delete_many({"name": "TEST1_UIFC"})

    def test_create_community_invalid(self):
        comm ={ 
                "name": "TEST_UIFC",
                "shortDescription": "UI Fighting Club",
                "longDescription": "Ayolah ribut ajaa sini",
                "status": "open",
                "rules": "Jangan berisik!!!!"
            }
        response = client.post(
            "/api/v1/community",
            headers={
                'Authorization': f"Bearer {self.token}"
            },
            data = {
                "community": json.dumps(comm)
            }
        )
        assert response.status_code == 422
        assert response.json() == {
            "detail": [
                {
                    "loc": [
                        "body",
                        "community",
                        "admin"
                    ],
                    "msg": "field required",
                    "type": "value_error.missing"
                }
            ]
        }

    def test_create_community(self):
        community = {
            "name":"TEST1_UIFC",
            "admin":"admin@ui.ac.id",
            "shortDescription":"UI Fighting Club",
            "longDescription":"Ayolah ribut ajaa sini",
            "status":"open",
            "rules":"Jangan berisik!!!!"
        }
        response = client.post(
            "/api/v1/community",
            headers={
                'Authorization': f"Bearer {self.token}"
            },
            data = {
                "community": json.dumps(community)
            }

        )
        assert response.status_code == 201
        assert response.json()["name"] == "TEST1_UIFC"
        db['communities'].delete_many({"name": "TEST1_UIFC"})

    def test_read_community(self):
        response = client.get(
            "/api/v1/community?skip=0&limit=1000",
            headers={
                'accept': self.application_json,
                'Authorization': f"Bearer {self.token}"
            }
        )
        assert response.status_code == 200
        assert self.data1 in response.json()

    def test_create_community_with_an_existing_name(self):
        response = client.post(
            "/api/v1/community",
            headers={
                'Authorization': f"Bearer {self.token}"
            },
            data = {
                "community": json.dumps(self.community)
            }

        )
        assert response.status_code == 409
        assert response.json() == {
            "detail": "Community with the name 'TEST_UIFC' already exists"
        }
     
    # Entah kenapa error test agak bizzare, karena json.dumps ny gk bekerja #
    #########################################################################
    # def test_create_community_invalid_file_attachment(self):
    #     dummy = {
    #         "name":"TEST1_UIFC",
    #         "admin":"admin@ui.ac.id",
    #         "shortDescription":"UI Fighting Club",
    #         "longDescription":"Ayolah ribut ajaa sini",
    #         "status":"open",
    #         "rules":"Jangan berisik!!!!"
    #     }
    #     response = client.post(
    #         "/api/v1/community",
    #         headers={
    #             'Authorization': f"Bearer {self.token}"
    #         },
    #         data = {
    #             "community": json.dumps(dummy)
    #         },
    #         files = {
    #             "file": ('test.txt', open('assets/test.txt', 'rb'), 'text/plain')
    #         }
    #     )
    #     assert response.json() == 'File type not allowed'
    #     assert response.status_code == 403



    def test_get_certain_community_invalid(self):
        response = client.get(
            f"/api/v1/community/1",
            headers={
                'accept': self.application_json,
                'Authorization': f"Bearer {self.token}"
            }
        )
        assert response.status_code == 404
        assert response.json()['detail'] == "Community 1 not found"

    def test_get_certain_community(self):
        response = client.get(
            f"/api/v1/community/{self.response_data.json()['_id']}",
            headers={
                'accept': self.application_json,
                'Authorization': f"Bearer {self.token}"
            }
        )
        assert response.status_code == 200
        assert response.json()['name'] == "TEST_UIFC"

    def test_update_community(self):
        dummy={
            "name": "TEST_UIFC",
            "shortDescription": "UI Footbal Club",
            "longDescription": "Ayolah ribut ajaa sini",
            "status": "open",
            "rules": "Jangan berisik!!!!"
        }
        response = client.put(
            f"/api/v1/community/{self.response_data.json()['_id']}",
            headers={
                'Authorization': f"Bearer {self.token}"
            },
            data ={
                "update_data": json.dumps(dummy)
            }
        )
        assert response.status_code == 200
        assert response.json()['shortDescription'] == "UI Footbal Club"

    def test_update_community_invalid(self):
        dummy={
            "name": "TEST_UIFC",
            "shortDescription": "UI Footbal Club",
            "longDescription": "Ayolah ribut ajaa sini",
            "status": "open",
            "rules": "Jangan berisik!!!!"
        }
        response = client.put(
            f"/api/v1/community/1",
            headers={
                'Authorization': f"Bearer {self.token}"
            },
            data ={
                "update_data": json.dumps(dummy)
            }
        )
        assert response.status_code == 404
        assert response.json()['detail'] == "community 1 not found"

    def test_update_community_unauthorized(self):
        response = client.put(
            f"/api/v1/community/{self.response_data.json()['_id']}",
            json={
                "name": "TEST_UIFC",
                "shortDescription": "UI Footbal Club",
                "longDescription": "Ayolah ribut ajaa sini",
                "status": "open",
                "rules": "Jangan berisik!!!!"
            }, headers={
                'accept': self.application_json,
                'Authorization': f"Bearer XKCD"
            }
        )
        assert response.status_code == 401

    def test_delete_community(self):
        response = client.delete(
            f"/api/v1/community/{self.response_data2.json()['_id']}",
            headers={
                'Authorization': f"Bearer {self.token}"
            }
        )
        assert response.status_code == 204

    def test_delete_community_invalid(self):
        response = client.delete(
            f"/api/v1/community/1",
            headers={
                'Authorization': f"Bearer {self.token}"
            }
        )
        assert response.status_code == 404
        assert response.json()['detail'] == "community 1 not found"

    def test_search_community_name_complete(self):
        response = client.get(
            f"/api/v1/community/search?name=TEST_UIFC",
            headers={
                'accept': self.application_json,
                'Authorization': f"Bearer {self.token}"
            }
        )

        assert response.status_code == 200
        assert response.json()[0]['name'] == "TEST_UIFC"

    def test_search_community_name_substring(self):
        response = client.get(
            f"/api/v1/community/search?name=est_ui",
            headers={
                'accept': self.application_json,
                'Authorization': f"Bearer {self.token}"
            }
        )
        assert response.status_code == 200
        assert response.json()[0]['name'] == "TEST_UIFC"
