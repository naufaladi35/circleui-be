from datetime import datetime
from dotenv import load_dotenv

from api.repository.repository import connect
from api.model.PH_Event.event import Event

load_dotenv()
db = connect()

event_collection = db['event']


async def get_items(skip, limit):
    return await event_collection.find(skip=skip, limit=limit).to_list(1000)

async def get_items_by_name(name, skip, limit):
    query = {
        "name": {
            "$regex": name,
            "$options": "i"
        }
    }
    return await event_collection.find(query, skip=skip, limit=limit).to_list(1000)

async def get_item(id: str):
    return await event_collection.find_one({'_id': id})

async def get_items_by_month(month, year, skip, limit):
    month_year = {
        "dateTime":{
            "$regex": f"{year}-{month}",
            "$options": "i"
        }
    }
    return await event_collection.find(month_year, skip=skip, limit=limit).to_list(1000)

async def insert_item(content: Event):
    return await event_collection.insert_one(content)


async def update_item(event: Event, id: str):
    return await event_collection.update_one({'_id': id}, {'$set': event})


async def delete_item(id: str):
    return await event_collection.delete_one({'_id': id})

async def event_bookmark(user_email: str, id: str):
    update_result = await db["user"].update_one({"email": user_email}, {"$push": {"eventEnrolled": id}})
    return update_result

async def event_unbookmark(user_email: str, id: str):
    update_result = await db["user"].update_one({"email": user_email}, {"$pull": {"eventEnrolled": id}})
    return update_result