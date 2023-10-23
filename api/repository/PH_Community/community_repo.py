import json
from ..repository import connect
from ...model.PH_Community.community_models import *

db = connect()


async def create_new_community(community: CommunityModel):
    return await db['communities'].insert_one(community)


async def find_community_with_name(name):
    return await db['communities'].find_one({'name': name})


async def find_new_community(new_community):
    return await db['communities'].find_one({"_id": new_community.inserted_id})


async def get_all_communities_from_db(skip, limit):
    return await db["communities"].find(skip=skip, limit=limit).to_list(1000)


async def get_certain_community_from_db(id: str):
    result = await db["communities"].find_one({"_id": id})
    return result


async def update_community_from_db(id: str, data: dict):
    update_result = await db["communities"].update_one({"_id": id}, {"$set": data})
    return update_result


async def delete_one_community_from_db(id: str):
    delete_result = await db["communities"].delete_one({"_id": id})
    return delete_result


async def get_community_with_name(name: str, skip: int, limit: int):
    query = {
        "name": {
            "$regex": name,
            "$options": "i"
        }
    }
    result = await db["communities"].find(query, skip=skip, limit=limit).to_list(1000)
    return result


async def join_community_add_user_to_community(user_email: str, id: str):
    update_result = await db["communities"].update_one({"_id": id}, {"$push": {"pendingMembers": user_email}})
    return update_result


async def add_community_to_user(user_email: str, id: str):
    update_result = await db["user"].update_one({"email": user_email}, {"$push": {"communityEnrolled": id}})
    return update_result

async def leave_community_remove_user_from_community(user_email: str, id: str):
    delete_result = await db["communities"].update_one({"_id": id}, {"$pull": {"publicMembers": user_email}})
    return delete_result

async def leave_community_remove_community_from_user(user_email: str, id: str):
    delete_result = await db["user"].update_one({"email": user_email}, {"$pull": {"communityEnrolled": id}})
    return delete_result