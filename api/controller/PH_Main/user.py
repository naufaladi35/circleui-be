from fastapi import APIRouter, Depends, Security, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm

from api.model.PH_Main import user, token
from api.service.PH_Main import user as user_service
from typing import Optional


router = APIRouter(
    prefix = '/api/v1',
    tags = ['auth'],
)

@router.get('/users/me')
async def read_users_me(current_user: user.User = Security(user_service.get_current_active_user, scopes = ['me'])):
    return current_user

@router.get('/users')
async def get_users(skip: int = 0, limit: int = 10, current_user: user.User = Security(user_service.get_current_active_user, scopes = ['users'])):
    users = await user_service.get_users(skip, limit)
    result = {
        'accessed_by': f"{current_user['user']['username']}",
        'content': users
    }
    return result

@router.put('/users/me/update')
async def update_user_me(form_data: user.updateUser, 
    file: Optional[UploadFile] = File(None), 
    current_user: user.User = Security(user_service.get_current_active_user, scopes = ['me'])):
    print(form_data)
    return await user_service.update_user(form_data, file, current_user)

@router.get('/users/{email}')
async def get_user_by_email_controller(    
    email: str,
    current_user: user.User = Security(user_service.get_current_active_user, scopes=['me'])):
    return await user_service.get_user_by_email(email)

@router.post('/register')
async def register_user(user: user.User):
    return await user_service.register_user(user)

@router.post('/login', response_model = token.Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    return await user_service.get_user_token(form_data)

@router.get('/logout')
async def logout(current_user: user.User = Security(user_service.get_current_active_user, scopes = ['logout'])):
    user_token = await user_service.delete_user_token(current_user['token'])
    result = {
        'access_token': False,
        'token_type': None,
        'status': user_token.acknowledged
    }
    return result

    