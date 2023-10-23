from ...model.PH_Community.announcement_models import AnnouncementModel
from ...model.PH_Main.user import User
from ...repository.PH_Community.announcement_repo import *
from fastapi.encoders import jsonable_encoder
from fastapi import Body, HTTPException, status
from pydantic import Field
from typing import Optional

async def create_announcement(announcement:AnnouncementModel=Body(...), admin: str=Field(...), id_community: str=Field(...)):
    announcement = jsonable_encoder(announcement)
    announcement['communityId'] = id_community
    # TODO: Bikin buat identifikasi kalo dia admin
    new_announcement = await create_new_announcement(announcement)
    created_announcement = await find_announcement(new_announcement)
    return created_announcement

async def get_certain_announcement_from_community_id(id_community:str):
    announcements = await get_certain_announcement_from_community_id_db(id_community)
    community = await get_certain_community_from_db(id_community)
    if(community is not None):
        return announcements

async def get_all_announcements():
    announcements = await get_all_announcement_from_db()
    return announcements

async def update_announcement(id:str, data:dict, current_user:Optional[str] = None):
    user = jsonable_encoder(current_user)
    current_user_id = user['user']['_id']
    await update_announcement_from_db(id, data, current_user_id)
    if(update_result := await get_certain_announcement_from_db(id)) is not None:
        return update_result

async def delete_announcement(id:str, current_user:Optional[str] = None):
    user = jsonable_encoder(current_user)
    current_user_id = user['user']['_id']
    delete_result = await delete_certain_announcement_from_db(id, current_user_id)
    if delete_result.deleted_count == 1:
        return True
