import pytz
import cloudinary
import cloudinary.uploader
from typing import Optional
from datetime import datetime
from fastapi import status, UploadFile
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from api.model.PH_Main.user import User
from api.model.PH_Community.post import Post
from api.repository.PH_Main import user as user_repository
from api.repository.PH_Community import post as post_repository

async def get_posts(community_id: str, skip: int = 0, limit: int = 10):
    return await post_repository.get_items(community_id, skip, limit)

async def get_post(id: str):
    return await post_repository.get_item(id)

async def create_post(form_data: Post, file: Optional[UploadFile], creator: str):
    now = datetime.now().astimezone(pytz.timezone('Asia/Jakarta')).isoformat(timespec='seconds')

    post = jsonable_encoder(form_data)
    post['creator'] = creator
    post['createdAt'] = now
    post['updatedAt'] = now

    if file and file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.svg')):
        upload_file = cloudinary.uploader.upload(
            file.file,
            folder = 'post_assets',
            allowed_formats = ['jpg', 'png', 'jpeg', 'svg']
        )
        url = upload_file.get('secure_url')
        post['attachment_url'] = url
    elif file and (not file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.svg'))):
        return JSONResponse(
            status_code = 403,
            content = 'File type not allowed'
        )

    insert_post = await post_repository.insert_item(content = post)
    status_code = status.HTTP_201_CREATED
    content = {
        'status': 'accepted',
        'acknowledged': insert_post.acknowledged,
        'inserted_id': insert_post.inserted_id
    }
    return JSONResponse(
        status_code = status_code,
        content = content
    )

async def toggle_like(liker: str, id: str):
    message = ''
    now = datetime.now().astimezone(pytz.timezone('Asia/Jakarta')).isoformat(timespec='seconds')

    post = await post_repository.get_item(id)
    print(post)
    if post and (liker not in post['userLiked']):
        post['likesCounter'] += 1
        post['userLiked'].append(liker)
        message = 'liked'
    elif post and (liker in post['userLiked']):
        post['likesCounter'] -= 1
        post['userLiked'].remove(liker)
        message = 'unliked'
    else:
        return JSONResponse(
            status_code = status.HTTP_404_NOT_FOUND,
            content = {
                'status': 'not found',
                'message': 'post is not found'
            }
        )
    
    post['updatedAt'] = now
    await post_repository.update_item(post, id)
    content = {
        'message': message
    }
    return JSONResponse(
        status_code = status.HTTP_200_OK,
        content = content
    )

async def update_post(updater: str, form_data: Post, id: str):
    status_code = ''
    content = ''
    now = datetime.now().astimezone(pytz.timezone('Asia/Jakarta')).isoformat(timespec='seconds')

    post = await post_repository.get_item(id)
    if post and (post['creator'] == updater):
        update = jsonable_encoder(form_data)
        update['updatedAt'] = now
        update_post = await post_repository.update_item(update, id)
        if update_post:
            status_code = status.HTTP_200_OK
            content = {
                'status': 'updated',
                'message': 'your post is successfully updated'
            }
    elif post and (post['creator'] != updater):
        status_code = status.HTTP_403_FORBIDDEN
        content = {
            'status': 'prohibited',
            'message': 'you are not the creator of this post'
        }
    else:
        status_code = status.HTTP_404_NOT_FOUND
        content = {
            'status': 'not found',
            'message': 'post is not found'
        }
    
    return JSONResponse(
        status_code = status_code,
        content = content
    )

async def delete_post(deleter: str, id: str):
    status_code = ''
    content = ''
    post = await post_repository.get_item(id)

    if post and (post['creator'] == deleter):
        delete_post = await post_repository.delete_item(id)
        status_code = status.HTTP_200_OK
        content = {
            'status': 'deleted',
            'acknowledged': delete_post.acknowledged,
            'deleted_count': delete_post.deleted_count
        }
    elif post and (post['creator'] != deleter):
        status_code = status.HTTP_403_FORBIDDEN
        content = {
            'status': 'forbidden',
            'message': 'you are not the creator of this post'
        }
    else:
        status_code = status.HTTP_404_NOT_FOUND
        content = {
            'status': 'not found',
            'message': 'post is not found'
        }
    
    return JSONResponse(
        status_code = status_code,
        content = content
    )
