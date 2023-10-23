from typing import Optional
from fastapi import APIRouter, Security, File, UploadFile

from api.model.PH_Main.user import User
from api.model.PH_Community.post import Post
from api.service.PH_Main import user as user_service
from api.service.PH_Community import post as post_service
from api.service.PH_Community import post_admin as post_admin_service

router = APIRouter(
    prefix = '/api/v1',
    tags = ['post'],
)

@router.get('/posts/{community_id}')
async def get_community_posts(
    community_id: str, 
    skip: int = 0, 
    limit: int = 10, 
    current_user: User = Security(user_service.get_current_active_user, scopes = ['me', 'logout'])
):
    posts = await post_service.get_posts(community_id, skip, limit)
    result = {
        'accessed_by': f"{current_user['user']['username']}",
        'content': posts
    }
    return result

@router.get('/post/{id}')
async def get_specific_post(
    id: str,
    current_user: User = Security(user_service.get_current_active_user, scopes = ['me', 'logout'])
):
    post = await post_service.get_post(id)
    result = {
        'accessed_by': f"{current_user['user']['username']}",
        'content': post
    }
    return result

@router.post('/post')
async def create_post(
    form_data: Post,
    file: Optional[UploadFile] = File(None),
    current_user: User = Security(user_service.get_current_active_user, scopes = ['me', 'logout'])
):
    return await post_service.create_post(form_data, file, current_user['user']['email'])

@router.post('/post/{id}/toggle-like')
async def toggle_like(
    id: str,
    current_user: User = Security(user_service.get_current_active_user, scopes = ['me', 'logout'])
):
    return await post_service.toggle_like(current_user['user']['email'], id)

@router.put('/post/{id}')
async def update_post(
    id: str,
    form_data: Post,
    current_user: User = Security(user_service.get_current_active_user, scopes = ['me', 'logout'])
):
    return await post_service.update_post(current_user['user']['email'], form_data, id)

@router.delete('/post/{id}')
async def delete_post(
    id: str,
    current_user: User = Security(user_service.get_current_active_user, scopes = ['me', 'logout'])
):
    return await post_service.delete_post(current_user['user']['email'], id)

@router.delete('/post/{id}/admin-delete')
async def delete_post(
    id: str,
    current_user: User = Security(user_service.get_current_active_user, scopes = ['me', 'logout'])
):
    return await post_admin_service.admin_delete_post(current_user['user']['email'], id)