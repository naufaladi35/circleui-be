from fastapi import APIRouter, Body, Security, status
from ...service.PH_Community.community_service import *
from ...model.PH_Community.community_models import *
from fastapi.responses import JSONResponse
from fastapi import FastAPI, Body, HTTPException, status,  File
from api.model.PH_Main import user, token
from api.service.PH_Main import user as user_service


router = APIRouter(
    prefix='/api/v1',
    tags=['community'],
)


@router.post('/community')
async def create_community_controller(
    community: CommunityModel,
    file: Optional[UploadFile] = File(None),
    current_user: user.User = Security(
        user_service.get_current_active_user, scopes=['me'])
):
    user_email = current_user['user']['email']
    content = await create_community(community,file, user_email)

    return JSONResponse(status_code=status.HTTP_201_CREATED, content=content)


@router.get('/community')
async def get_communities_controller(
    current_user: user.User = Security(
        user_service.get_current_active_user, scopes=['me']),
        skip : int = 0,
        limit : int = 10
):
    communities = await get_all_communities(skip, limit)
    return communities


@router.get('/community/search')
async def search_communities_controller(
    name: str,
    current_user: user.User = Security(
        user_service.get_current_active_user, scopes=['me']),
    skip : int =0,
    limit : int = 10
):
    communities = await get_communities_by_name(name, skip, limit)
    return communities


@router.get('/community/{id}')
async def get_certain_community_controller(
    id: str,
    current_user: user.User = Security(
        user_service.get_current_active_user, scopes=['me'])
):
    community = await get_certain_community(id)
    return community


@router.put("/community/{id}")
async def update_community_controller(
    id: str,
    update_data: UpdateCommunityModel,
    file: Optional[UploadFile] = File(None),
    current_user: user.User = Security(
        user_service.get_current_active_user, scopes=['me'])
):
    user_email = current_user['user']['email']
    update_data = jsonable_encoder(update_data)
    community = await update_community(user_email, id, file, update_data)
    if(community is not None):
        return community



@router.delete("/community/{id}")
async def delete_community_controller(
    id: str,
    current_user: user.User = Security(
        user_service.get_current_active_user, scopes=['app-admin'])
):
    delete_successfull = await delete_community(id)
    if delete_successfull == True:
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"community {id} not found")


@router.put("/community/{id}/join")
async def join_community_controller(
    id: str,
    current_user: user.User = Security(
        user_service.get_current_active_user, scopes=['me'])
):
    user_email = current_user['user']['email']
    community = await join_community(user_email, id)
    if(community is not None):
        return community


@router.put("/community/{id}/manage_member")
async def manage_member_controller(
    id: str,
    data: ManageMemberModel = Body(...),
    current_user: user.User = Security(
        user_service.get_current_active_user, scopes=['me'])
):
    admin_email = current_user['user']['email']
    return await manage_member(admin_email, id, data)


@router.put("/community/{id}/leave")
async def leave_community_controller(
    id: str,
    current_user: user.User = Security(
        user_service.get_current_active_user, scopes=['me'])
):
    user_email = current_user['user']['email']
    delete_successfull = await leave_community(user_email, id)
    return delete_successfull
