import os, pytz
from datetime import datetime, timedelta
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends, HTTPException, Security, status,  UploadFile
from typing import Optional
import cloudinary
import cloudinary.uploader
from api.model.PH_Main import user
from api.model.PH_Main.token import Token
from api.model.PH_Main.tokenData import TokenData
from api.repository.PH_Main import user as user_repository

async def register_user(user: user.User):
    now = datetime.now().astimezone(pytz.timezone('Asia/Jakarta')).isoformat(timespec='seconds')
    status_code = ''
    content = ''

    user = jsonable_encoder(user)

    user['joinedAt'] = now
    user['updatedAt'] = now

    check_email = user['email'].split('@')
    if check_email[1] != 'ui.ac.id':
        status_code = status.HTTP_403_FORBIDDEN
        content = {
            'status': 'rejected',
            'message': "This is not valid UI email"
        }
        return JSONResponse(
            status_code = status_code,
            content = content
        )

    check_is_field_valid = await user_repository.is_field_exist(
        username = user['username'],
        email = user['email'],
        ui_identity_number = user['uiIdentityNumber']
    )
    if check_is_field_valid is None:
        insert_user = await user_repository.insert_item(user = user)
        status_code = status.HTTP_201_CREATED
        content = {
            'status': 'accepted',
            'acknowledged': insert_user.acknowledged,
            'inserted_id': insert_user.inserted_id
        }
    else:
        status_code = status.HTTP_403_FORBIDDEN
        content = {
        'status': 'rejected',
        'message': f"either username {user['username']} or email {user['email']} or NPM {user['uiIdentityNumber']} is exist. Please check again!"
        }

    return JSONResponse(
        status_code = status_code,
        content = content
    )


async def update_user(form_data: user.updateUser, file:Optional[UploadFile], current_user: user.User):
    status_code = ''
    content = ''

    update_user = jsonable_encoder(form_data)
    user = jsonable_encoder(current_user)
    current_user_id = user['user']['_id']

    if file is not None:
        if file and file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.svg')):
            upload_file = cloudinary.uploader.upload(
                file.file,
                folder = 'profile_assets',
                allowed_formats = ['jpg', 'png', 'jpeg', 'svg']
            )
            url = upload_file.get('secure_url')
            update_user['image'] = url
        elif file and (not file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.svg'))):
            return JSONResponse(
                status_code = 403,
                content = 'File type not allowed'
            )
    else:
        update_user['image'] = user['user']['image']

    updated_user = await user_repository.update_item(data=update_user, id=current_user_id)
    if updated_user:
        status_code = status.HTTP_200_OK
        content = {
            'status': 'accepted',
            'message': 'Update profile successful'
        }
    else:
        status_code = status.HTTP_403_FORBIDDEN
        content = {
            'status': 'rejected',
            'message': 'Incomplete field'
        }

    return JSONResponse(
        status_code=status_code,
        content=content
    )
    
async def get_user_by_email(user_email: str):
    user = await user_repository.get_specific_user_by_email(user_email)
    if user is not None:
        return user
    else:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = f"email {user_email} is not exist",
            headers = {'WWW-Authenticate': 'Bearer'}
        )

async def get_user_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await user_repository.get_specific_item(username = form_data.username)
    if user is None:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = f"Incorrect username, {form_data.username} is not exist",
            headers = {'WWW-Authenticate': 'Bearer'}
        )

    verify_password = user_repository.verify_password(form_data.password, user['password'])
    if not verify_password:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = f"Incorrect password, {form_data.password} did not match with {form_data.username}",
            headers = {'WWW-Authenticate': 'Bearer'}
        )
  
    access_token_expires = timedelta(minutes = int(os.environ['ACCESS_TOKEN_EXPIRE_MINUTES']))
    access_token = await user_repository.create_access_token(
        data = { 'sub': user['username'], 'scopes': form_data.scopes },
        expires_delta = access_token_expires
    )

    token = Token(
        access_token = str(access_token),
        token_type = 'bearer'
    )
    await user_repository.insert_item(token = jsonable_encoder(token))

    token_data = TokenData(
        username = user['username'],
        scopes = form_data.scopes
    )
    check_before_insert = await user_repository.get_specific_item(token_data = token_data.username)
    if not check_before_insert:
        await user_repository.insert_item(token_data = jsonable_encoder(token_data))

    return { 'access_token': access_token, 'token_type': 'bearer' }

async def delete_user_token(token: str):
    return await user_repository.delete_user_token(token)

async def get_users(skip: int = 0, limit: int = 10):
    return await user_repository.get_all_item(skip, limit)

async def get_current_active_user(current_user: user.User = Security(user_repository.get_current_user, scopes = ['me'])):
    return current_user
  
