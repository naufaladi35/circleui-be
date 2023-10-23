from ..repository import connect
from fastapi import HTTPException, status
from ...model.PH_Community.announcement_models import *

db = connect()

async def create_new_announcement(announcement: AnnouncementModel):
    return await db['announcement'].insert_one(announcement)

async def find_announcement(new_announcement):
    return await db['announcement'].find_one({"_id":new_announcement.inserted_id})

async def get_certain_announcement_from_community_id_db(id_community:str):
    result = await db['announcement'].find({"communityId":id_community}).sort([('createdAt', -1),('_id', -1)]).to_list(1000)
    return result

async def get_all_announcement_from_db():
    return await db['announcement'].find(skip=0,limit=0).to_list(1000)

async def get_certain_announcement_from_db(id:str):
    result = await db['announcement'].find_one({"_id":id})
    return result

async def get_certain_community_from_db(id:str):
    if(result := await db["communities"].find_one({"_id": id})) is not None:
        return result
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"community {id} not found"
        )

async def update_announcement_from_db(id: str, data:dict,id_user:Optional[str] = None):
    try:
        user = await db["user"].find_one({'_id':id_user})
        announcement = await get_certain_announcement_from_db(id)
        id_community = announcement['communityId']
        community = await get_certain_community_from_db(id_community)
        if(community is not None):
            if(community['admin'] == user['email']):
                update_result = await db['announcement'].update_one({"_id":id},{"$set":data})
                return update_result
            else:
                raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED,detail=f"You're not admin of {community['name']}")
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"community {id_community} not found"
             )

    except(TypeError):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"announcement {id} not found"
        )

async def delete_certain_announcement_from_db(id:str, id_user:Optional[str] = None):
    try:
        user = await db["user"].find_one({'_id':id_user})
        announcement = await get_certain_announcement_from_db(id)
        print(announcement)
        id_community = announcement['communityId']
        print(id_community)
        community = await get_certain_community_from_db(id_community)
        print(community)
        if(community is not None):
            if(community['admin'] == user['email']):
                delete_result = await db['announcement'].delete_one({"_id":id})
                return delete_result
            else:
                raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED,detail=f"You're not admin of {community['name']}")
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"community {id_community} not found"
             )
    except(TypeError):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"announcement {id} not found"
        )


