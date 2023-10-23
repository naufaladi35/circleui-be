from cmath import e
from ...model.PH_Community.comment_models import *
from ...service.PH_Community.post import get_post
from ...service.PH_Community.community_service import get_certain_community_from_db
from ..repository import connect
from fastapi import HTTPException, status

db = connect()

async def create_new_comment(comment: CommentModel):
    return await db['comment'].insert_one(comment)

async def find_comment(new_comment):
    return await db['comment'].find_one({"_id":new_comment.inserted_id})

async def get_certain_comment_from_post_id_db(id_post:str):
    result = await db['comment'].find({"postId":id_post}).to_list(1000)
    return result

async def get_all_comments_from_db():
    return await db['comment'].find(skip=0, limit=0).to_list(1000)

async def get_certain_comment_from_db(id: str):
    result = await db['comment'].find_one({"_id":id})
    return result

async def delete_certain_comment_from_db(id: str, id_user: Optional[str] = None):
    try:
        user = await db["user"].find_one({'_id': id_user})
        comment = await get_certain_comment_from_db(id)
        post = await get_post(comment['postId'])
        community = await get_certain_community_from_db(post['communityId'])
        if (comment['email'] == user['email']):
            return await db["comment"].delete_one({"_id": id})
        elif (user['email'] == community['admin']):
            return await db["comment"].delete_one({"_id": id})
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="not enough permission")
    except (TypeError):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"comment {id} not found")

async def update_comment_from_db(id: str, data: dict, id_user: Optional[str] = None):
    try:
        user = await db["user"].find_one({'_id': id_user})
        comment = await get_certain_comment_from_db(id)
        if (comment['email'] ==  user['email']):
            update_result = await db["comment"].update_one({"_id": id}, {"$set": data})
            return update_result
        else:
            raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED)
    except (TypeError):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"comment {id} not found")