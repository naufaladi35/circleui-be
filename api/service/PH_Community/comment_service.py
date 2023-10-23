from ...model.PH_Community.comment_models import CommentModel
from ...model.PH_Main.user import User
from ...repository.PH_Community.comment_repo import create_new_comment, find_comment, get_certain_comment_from_db, get_certain_comment_from_post_id_db, get_all_comments_from_db, delete_certain_comment_from_db, update_comment_from_db
from fastapi.encoders import jsonable_encoder
from fastapi import Body, HTTPException, status
from pydantic import Field
from typing import Optional

async def create_comment(comment: CommentModel = Body(...), creator: User= Body(...), id_post: str= Field(...)):
    comment = jsonable_encoder(comment)
    comment['email'] = creator['user']['email']
    comment['username'] = creator['user']['username']
    comment['postId'] = id_post
    new_comment = await create_new_comment(comment)
    created_comment = await find_comment(new_comment)
    return created_comment

async def get_certain_comment_from_post_id(id_post:str):
    comments = await get_certain_comment_from_post_id_db(id_post)
    if(len(comments)) > 0 :
        return comments
    raise HTTPException(status_code=404, detail=f"Post {id_post} not found")

async def get_all_comments():
    comments = await get_all_comments_from_db()
    return comments

async def delete_comment(id: Optional[str] = None, current_user: Optional[User] = None):
    try:    
        user = jsonable_encoder(current_user)
        current_user_id = user['user']['_id']
        delete_result = await delete_certain_comment_from_db(id, id_user=current_user_id)
        if delete_result.deleted_count == 1:
            return True
    except (AttributeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=f"not enough permission")

async def update_comment(id: str, data: dict, current_user: Optional[User] = None):
    user = jsonable_encoder(current_user)
    current_user_id = user['user']['_id']
    await update_comment_from_db(id, data, current_user_id)
    if (update_result := await get_certain_comment_from_db(id)) is not None:
        return update_result