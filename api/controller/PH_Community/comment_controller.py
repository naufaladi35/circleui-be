from fastapi import APIRouter, Body, Security, status
from ...service.PH_Community.comment_service import *
from ...model.PH_Community.comment_models import *
from fastapi.responses import JSONResponse
from fastapi import Body, HTTPException, status
from api.model.PH_Main import user,token
from api.service.PH_Main import user as user_service

router = APIRouter(
    prefix='/api/v1',
    tags=['comment'],
)

@router.post('/comment/{id_post}')
async def create_comment_controller(
    id_post: str,
    comment: CommentModel = Body(...),
    current_user: user.User = Security(
        user_service.get_current_active_user, scopes=['me']
        )
    ):
    content = await create_comment(comment, current_user,id_post)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=content)

@router.get('/comment/{id_post}/post')
async def get_certain_comment_from_post_controller(
    id_post: str,
    current_user: user.User = Security(
    user_service.get_current_active_user, scopes=['me'])
    ):
    comments = await get_certain_comment_from_post_id(id_post)
    return comments

@router.get('/comment')
async def get_comment_controller(
    current_user: user.User = Security(
    user_service.get_current_active_user, scopes=['me'])
    ):
    comments = await get_all_comments()
    return comments


@router.delete("/comment/{id}")
async def delete_comment_controller(
        id: str,
        current_user: user.User = Security(
        user_service.get_current_active_user, scopes=['me'])
        ):
    
    delete_sucessfull = await delete_comment(id, current_user)
    if delete_sucessfull == True:
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/comment/{id}")
async def update_comment_controller(
    id: str,
    update_data: UpdateCommentModel = Body(...),
    current_user: user.User = Security(
        user_service.get_current_active_user, scopes=['me']
    )
):
    update_data = jsonable_encoder(update_data)
    comment = await update_comment(id, update_data, current_user)
    if comment is not None:
        return comment