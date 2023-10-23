import pytz
from datetime import datetime
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends, HTTPException, Security, status

from api.model.PH_Main.user import User
from api.model.PH_Community.post import Post
from api.model.PH_Community.community_models import CommunityModel
from api.repository.PH_Main import user as user_repository
from api.repository.PH_Community import post as post_repository
from api.repository.PH_Community import community_repo

async def admin_delete_post(admin = str, id = str):
    post = await post_repository.get_item(id)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with the id of {id} not found"
         )
    community = await community_repo.get_certain_community_from_db(post['communityId'])
    if admin == community['admin']:
        delete_post = await post_repository.delete_item(id)
        return JSONResponse(
            status_code = status.HTTP_200_OK,
            content={
                'status': 'deleted by admin',
                'acknowledged': delete_post.acknowledged,
                'deleted_count': delete_post.deleted_count
            }
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not the admin of this community"
         )