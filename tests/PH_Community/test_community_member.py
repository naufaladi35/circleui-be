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
            username="admin_member_test",
            password="pplasikgaboong",
            name="Admin Community PPL",
            email="admin_member_test@ui.ac.id",
            description="Lyfe is never flat as a community admin",
            uiIdentityNumber="1984198469697071",
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
            {'username': 'admin_member_test'})

        cls.leave = User(
            username="intoodeep",
            password="pplasikgaboong",
            name="not Admin Community PPL",
            email="intoodeep@ui.ac.id",
            description="Lyfe is never flat as a community admin",
            uiIdentityNumber="190666666",
            faculty="faculty of Psychology",
            classOf="2010",
            linkedin="linkedin.com/admin_budackPPL",
            twitter="twitter.com/admin_budackPPL",
            instagram="instagram.com/admin_budackPPL",
            tiktok="tiktok.com/admin_budackPPL",
            communityEnrolled=[
            ],
            eventEnrolled=[
            ]
        )
        client.post(
            url=cls.register,
            json=jsonable_encoder(cls.leave)
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
                'username': 'admin_member_test',
                'password': 'pplasikgaboong',
                'scope': 'me users logout app-admin'
            }
        )
        self.token = response.json()['access_token']
        response = client.post(
            self.login,
            headers={
                'Content-Type': self.application_encoded
            },
            data={
                'username': 'intoodeep',
                'password': 'pplasikgaboong',
                'scope': 'me users logout app-admin'
            }
        )
        self.leave_token = response.json()['access_token']

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
            }
        )
        self.community_id = self.response_data.json()['_id']

        response = client.post(
            self.login,
            headers={
                'Content-Type': self.application_encoded
            },
            data={
                'username': 'not_admin_community_test_UI',
                'password': 'pplasikgaboong',
                'scope': 'me users logout app-admin'
            }
        )
        self.not_admin_token = response.json()['access_token']

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
                'Authorization': f"Bearer {self.not_admin_token}"
            }
        )
        client.get(
            url=self.logout,
            headers={
                'accept': self.application_json,
                'Authorization': f"Bearer {self.leave_token}"
            }
        )
        db['communities'].delete_many({"name": "TEST_UIFC"})
        db['communities'].delete_many({"name": "Delete_UIFC"})

    def test_join_community(self):
        response = client.put(
            f"/api/v1/community/{self.community_id}/join",
            headers={
                'accept': self.application_json,
                'Authorization': f"Bearer {self.not_admin_token}"
            },
        )
        assert response.status_code == 200
        assert "not-adminadmin@ui.ac.id" in response.json()['pendingMembers']

    def test_join_community_fail(self):
        response = client.put(
            f"/api/v1/community/XD/join",
            headers={
                'accept': self.application_json,
                'Authorization': f"Bearer {self.not_admin_token}"
            },
        )
        assert response.status_code == 404

    def test_approve_join_request(self):
        member_email = "test.approve@ui.ac.id"
        response = client.put(
            f"/api/v1/community/{self.community_id}/manage_member",
            json={
                "email": member_email,
                "option": "approve",
            }, headers={
                'accept': self.application_json,
                'Authorization': f"Bearer {self.token}"
            },
        )
        assert response.status_code == 200
        assert member_email in response.json()['publicMembers']
        assert member_email not in response.json()['pendingMembers']

    def test_reject_join_request(self):
        member_email = "test.deny@ui.ac.id"
        response = client.put(
            f"/api/v1/community/{self.community_id}/manage_member",
            json={
                "email": member_email,
                "option": "reject",
            }, headers={
                'accept': self.application_json,
                'Authorization': f"Bearer {self.token}"
            },
        )
        assert response.status_code == 200
        assert member_email not in response.json()['pendingMembers']
        assert member_email not in response.json()['publicMembers']

    def test_approve_join_request_failed(self):
        response = client.put(
            f"/api/v1/community/1/manage_member",
            json={
                "email": "test.deny@ui.ac.id",
                "option": "reject",
            }, headers={
                'accept': self.application_json,
                'Authorization': f"Bearer {self.token}"
            },
        )

        assert response.status_code == 404

    def test_approve_join_request_unauthorized(self):
        member_email = "test.deny@ui.ac.id"
        response = client.put(
            f"/api/v1/community/{self.community_id}/manage_member",
            json={
                "email": member_email,
                "option": "reject",
            }, headers={
                'accept': self.application_json,
                'Authorization': f"Bearer {self.not_admin_token}"
            },
        )
        assert response.status_code == 401

    def test_leave_community(self):
        response = client.put(
            f"/api/v1/community/{self.community_id}/leave",
            headers={
                'accept': self.application_json,
                'Authorization': f"Bearer {self.leave_token}"
            },
        )
        assert response.status_code == 200
        assert "intoodeep@ui.ac.id" not in response.json()['publicMembers']

    def test_leave_community_fail(self):
        response = client.put(
            f"/api/v1/community/XD/leave",
            headers={
                'accept': self.application_json,
                'Authorization': f"Bearer {self.leave_token}"
            },
        )
        assert response.status_code == 404

    def test_remove_member(self):
        member_email = "intoodeep@ui.ac.id"
        response = client.put(
            f"/api/v1/community/{self.community_id}/manage_member",
            json={
                "email": member_email,
                "option": "remove",
            }, headers={
                'accept': self.application_json,
                'Authorization': f"Bearer {self.token}"
            },
        )
        assert response.status_code == 200
        assert member_email not in response.json()['publicMembers']

    def test_remove_member_community_invalid(self):
        member_email = "intoodeep@ui.ac.id"
        response = client.put(
            f"/api/v1/community/XDDD/manage_member",
            json={
                "email": member_email,
                "option": "remove",
            }, headers={
                'accept': self.application_json,
                'Authorization': f"Bearer {self.token}"
            },
        )
        assert response.status_code == 404

    def test_remove_member_email_invalid(self):
        member_email = "h@ui.ac.id"
        response = client.put(
            f"/api/v1/community/{self.community_id}/manage_member",
            json={
                "email": member_email,
                "option": "remove",
            }, headers={
                'accept': self.application_json,
                'Authorization': f"Bearer {self.token}"
            },
        )
        assert response.status_code == 400
