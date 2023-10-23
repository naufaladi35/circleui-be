from urllib import response
from fastapi.testclient import TestClient
from app import app
from dotenv import load_dotenv
from api.repository.repository import connect
from unittest import TestCase
from api.model.PH_Main.user import User
from api.model.PH_Event.event import Event
from fastapi.encoders import jsonable_encoder
import json

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
            username="user_test_UI",
            password="pplasikgaboong",
            name="Event Organizer PPL",
            email="evorg@ui.ac.id",
            description="Lyfe is never flat as an event organizer",
            uiIdentityNumber="1984198470",
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
            username="user_test_UI_2",
            password="pplasikgaboong",
            name="Event Organizer PPL 2",
            email="evorg2@ui.ac.id",
            description="Lyfe is never flat as an event organizer 2",
            uiIdentityNumber="1984198471",
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
            {'username': 'user_test_UI'})

    @classmethod
    def tearDownClass(cls):
        # tearDownClass: Run once to clean up after all class methods has been executed.
        db['event'].delete_many({"name": "Kajian awal puasa"})
        db['event'].delete_many({"name": "Kajian akhir puasa"})
        db['user'].delete_one({'username': 'user_test_UI'})

    def setUp(self):
        # setUp: Run once for every test method to setup clean data.
        response = client.post(
            self.login,
            headers={
                'Content-Type': self.application_encoded
            },
            data={
                'username': 'user_test_UI',
                'password': 'pplasikgaboong',
                'scope': 'me users logout app-admin'
            }
        )
        self.token = response.json()['access_token']

        # CREATE EVENT
        self.event = {
            "name":"Kajian awal puasa",
            "status":"open",
            "description":"Membahas amalan yang dapat dilakukan selama ramadan",
            "dateTime":"2022-04-07T10:30:00.000Z",
            "location":"Masjid UI",
            "contact":"081857463214",
            "link":"string",
            "price":"Free",
            "organizer":"evorg@ui.ac.id",
            "numberOfBookmark":0,
            "createdAt":"2022-04-03T10:30:00.000Z",
            "updatedAt":"2022-04-03T10:30:00.000Z"
        }
        self.event2 = {
            "name":"Kajian akhir puasa",
            "status":"open",
            "description":"Membahas amalan yang dapat dilakukan setelah ramadan",
            "dateTime":"2022-04-07T10:30:00.000Z",
            "location":"Masjid UI",
            "contact":"081857463214",
            "link":"string",
            "price":"Free",
            "organizer":"evorg@ui.ac.id",
            "numberOfBookmark":0,
            "createdAt":"2022-04-03T10:30:00.000Z",
            "updatedAt":"2022-04-03T10:30:00.000Z"
        }
        self.response_data = client.post(
            "/api/v1/event",
            headers={
                'Authorization': f"Bearer {self.token}"
            },
            data = {
                "form_data": json.dumps(self.event)
            },
            files = {
                "file": ('bentley.jpg', open('assets/bentley.jpg', 'rb'), 'image/jpeg')
            }
        )

        self.data1 = self.response_data.json()
        self.event_id = self.response_data.json()['inserted_id']



    def tearDown(self):
        # tearDown: Clean up run after every test method.
        client.get(
            url=self.logout,
            headers={
                'accept': self.application_json,
                'Authorization': f"Bearer {self.token}"
            }
        )

    def test_create_event_invalid(self):
        dum_event = {
                "name": "Kajian awal puasa",
                "status": "open",
                "description": "Membahas amalan yang dapat dilakukan selama ramadan",
                "location": "Masjid UI",
            }
        response = client.post(
            "/api/v1/event",
            headers={
                'accept': self.application_json,
                'Authorization': f"Bearer {self.token}"
            },
            data = {
                'form_data': json.dumps(dum_event)
            }
            
        )
        assert response.status_code == 422

    def test_create_event(self):
        response = client.post(
            "/api/v1/event",
            headers={
                'accept': self.application_json,
                'Authorization': f"Bearer {self.token}"
            },
            data = {
                "form_data": json.dumps(self.event2)
            }, 
        )
        assert response.status_code == 201
        assert response.json()['inserted_id'] is not None

    def test_get_all_event(self):
        response = client.get(
            "/api/v1/events",
            headers={
                'accept': self.application_json,
                'Authorization': f"Bearer {self.token}"
            }
        )
        assert response.status_code == 200

    def test_search_events(self):
        response = client.get(
            "/api/v1/events/search?name=Kajian",
            headers={
                'accept': self.application_json,
                'Authorization': f"Bearer {self.token}"
            }
        )
        assert response.status_code == 200

    def test_get_certain_event_invalid(self):
        response = client.get(
            f"/api/v1/event/1",
            headers={
                'accept': self.application_json,
                'Authorization': f"Bearer {self.token}"
            }
        )
        assert response.status_code == 404
        assert response.json()['detail'] == "event 1 not found"

    def test_get_certain_event(self):
        response = client.get(
            f"/api/v1/event/{self.event_id}",
            headers={
                'accept': self.application_json,
                'Authorization': f"Bearer {self.token}"
            }
        )
        assert response.status_code == 200
        assert response.json()['content']['name'] == "Kajian awal puasa"

    def test_update_event(self):
        dummy = {
            "_id": self.event_id,
            "name": "Kajian awal puasa",
            "status": "open",
            "description": "Membahas amalan yang dapat dilakukan selama ramadan",
            "dateTime": "2022-04-07T15:30:00.000Z",
            "location": "Mushola Fakultas Teknik",
            "contact": "081857463214",
            "link": "string",
            "price": "Free",
            "organizer": "evorg@ui.ac.id",
            "numberOfBookmark": 0,
            "createdAt": "2022-04-03T10:30:00.000Z",
            "updatedAt": "2022-04-04T18:30:00.000Z"
        }
        response = client.put(
            f"/api/v1/event/{self.event_id}",
            headers={
                'accept': self.application_json,
                'Authorization': f"Bearer {self.token}"
            },
            data = {
                "form_data":json.dumps(dummy)
            }
        )
        assert response.status_code == 200
        assert response.json()['message'] == "your event is successfully updated"

    def test_update_event_invalid(self):
        dummy={
            "name": "Kajian awal puasa",
            "status": "open",
            "description": "Membahas amalan yang dapat dilakukan selama ramadan",
            "dateTime": "2022-04-07T15:30:00.000Z",
            "location": "Mushola Fakultas Teknik",
            "contact": "081857463214",
            "link": "string",
            "price": "Free",
            "organizer": "evorg@ui.ac.id",
            "numberOfBookmark": 0,
            "createdAt": "2022-04-03T10:30:00.000Z",
            "updatedAt": "2022-04-04T18:30:00.000Z"
        } 
        response = client.put(
            f"/api/v1/event/2",
            headers={
                'accept': self.application_json,
                'Authorization': f"Bearer {self.token}"
            },
            data = {
                "form_data":json.dumps(dummy)
            }
        )
        assert response.status_code == 404
        assert response.json()['message'] == "event 2 not found"

    def test_update_event_forbidden(self):
        response2 = client.post(
            self.login,
            headers={
                'Content-Type': self.application_encoded
            },
            data={
                'username': 'user_test_UI_2',
                'password': 'pplasikgaboong',
                'scope': 'me users logout app-admin'
            }
        )
        self.token2 = response2.json()['access_token']
        dummy={
                "name": "Kajian awal puasa",
                "status": "open",
                "description": "Membahas amalan yang dapat dilakukan selama ramadan",
                "dateTime": "2022-04-07T15:30:00.000Z",
                "location": "Mushola Fakultas Teknik",
                "contact": "081857463214",
                "link": "string",
                "price": "Free",
                "organizer": "evorg@ui.ac.id",
                "numberOfBookmark": 0,
                "createdAt": "2022-04-03T10:30:00.000Z",
                "updatedAt": "2022-04-04T18:30:00.000Z"
            }
        response = client.put(
            f"/api/v1/event/{self.event_id}",
            headers={
                'accept': self.application_json,
                'Authorization': f"Bearer {self.token2}"
            },
            data = {
                "form_data": json.dumps(dummy)
            }
        )
        assert response.status_code == 403
        assert response.json()[
            'message'] == "you are not the organizer of this event"

    def test_delete_event(self):
        response = client.delete(
            f"/api/v1/event/{self.event_id}",
            headers={
                'Authorization': f"Bearer {self.token}"
            }
        )
        assert response.status_code == 204

    def test_delete_event_invalid(self):
        response = client.delete(
            f"/api/v1/event/1",
            headers={
                'Authorization': f"Bearer {self.token}"
            }
        )
        assert response.status_code == 404
        assert response.json()['message'] == "event 1 not found"

    def test_delete_event_forbidden(self):
        response2 = client.post(
            self.login,
            headers={
                'Content-Type': self.application_encoded
            },
            data={
                'username': 'user_test_UI_2',
                'password': 'pplasikgaboong',
                'scope': 'me users logout app-admin'
            }
        )
        self.token2 = response2.json()['access_token']
        response = client.delete(
            f"/api/v1/event/{self.event_id}",
            headers={
                'Authorization': f"Bearer {self.token2}"
            }
        )
        assert response.status_code == 403
        assert response.json()[
            'message'] == "you are not the organizer of this event"

    def test_bookmark_event(self):
        response = client.put(
            f"/api/v1/event/{self.event_id}/bookmark",
            headers={
                'accept': self.application_json,
                'Authorization': f"Bearer {self.token}"
            },
        )
        assert response.status_code == 200
        getuser = client.get(
            f"/api/v1/users/me",
            headers={
                'accept': self.application_json,
                'Authorization': f"Bearer {self.token}"
            },
        )
        assert self.event_id in getuser.json()['user']['eventEnrolled']

    def test_bookmark_event_invalid(self):
        response = client.put(
            f"/api/v1/event/XD/bookmark",
            headers={
                'accept': self.application_json,
                'Authorization': f"Bearer {self.token}"
            },
        )
        assert response.status_code == 404

    def test_unbookmark_event(self):
        response = client.put(
            f"/api/v1/event/{self.event_id}/unbookmark",
            headers={
                'accept': self.application_json,
                'Authorization': f"Bearer {self.token}"
            },
        )
        assert response.status_code == 200
        getuser = client.get(
            f"/api/v1/users/me",
            headers={
                'accept': self.application_json,
                'Authorization': f"Bearer {self.token}"
            },
        )
        assert self.event_id not in getuser.json()['user']['eventEnrolled']

    def test_unbookmark_event_invalid(self):
        response = client.put(
            f"/api/v1/event/XD/unbookmark",
            headers={
                'accept': self.application_json,
                'Authorization': f"Bearer {self.token}"
            },
        )
        assert response.status_code == 404
    
    def test_this_month_event(self):
        response = client.get(
            "/api/v1/this-months-events?current_month=05&current_year=2022&skip=0&limit=5",
            headers={
                'accept': self.application_json,
                'Authorization': f"Bearer {self.token}"
            }
        )
        assert response.status_code == 200
    
    def test_this_month_event_invalid(self):
        response = client.get(
            "/api/v1/this-months-events?current_month=15&current_year=2022&skip=0&limit=5",
            headers={
                'accept': self.application_json,
                'Authorization': f"Bearer {self.token}"
            }
        )
        assert response.status_code == 400
        assert response.json()['detail'] == "please enter valid month"
