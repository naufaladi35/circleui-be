from fastapi import APIRouter, Body, Security, status
from ...service.PH_Community.announcement_service import *
from ...model.PH_Community.announcement_models import *
from fastapi.responses import JSONResponse
from fastapi import Body, HTTPException, status
from api.model.PH_Main import user,token
from api.service.PH_Main import user as user_service

router = APIRouter(
    prefix='/api/v1',
    tags=['announcement'],
)

@router.post('/announcement/{id_community}')
async def create_announcement_controller(
    id_community: str,
    announcement: AnnouncementModel = Body(...),
    current_user: user.User = Security(
        user_service.get_current_active_user, scopes=['me']
        )
    ):
    content = await create_announcement(announcement, current_user['user']['email'],id_community)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=content)

@router.get('/announcement/{id_community}/community')
async def get_certain_announcement_from_community_controller(
    id_community: str,
    current_user: user.User = Security(
    user_service.get_current_active_user, scopes=['me'])
    ):
    announcements = await get_certain_announcement_from_community_id(id_community)
    return announcements

@router.get('/announcement')
async def get_announcement_controller(
    current_user: user.User = Security(
    user_service.get_current_active_user, scopes=['me'])
    ):
    announcements = await get_all_announcements()
    return announcements

@router.put('/announcement/{id}')
async def update_announcement_controller(
    id: str,
    update_data: UpdateAnnouncementModel = Body(...),
    current_user: user.User = Security(
        user_service.get_current_active_user, scopes=['me']
    )
):
    update_data = jsonable_encoder(update_data)
    announcement = await update_announcement(id, update_data, current_user)
    if announcement is not None:
        return announcement

@router.delete('/announcement/{id}')
async def delete_announcement_controller(
    id:str,
    current_user: user.User = Security(
        user_service.get_current_active_user, scopes=['me'])

):
    delete_result = await delete_announcement(id, current_user)
    if delete_result == True:
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content={"detail":f"announcement {id} has been deleted"})