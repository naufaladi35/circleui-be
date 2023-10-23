import os
from typing import Optional
from dotenv import load_dotenv
from jose import JWTError, jwt
from pydantic import ValidationError
from datetime import datetime, timedelta
from passlib.context import CryptContext
from fastapi.encoders import jsonable_encoder
from fastapi import Depends, HTTPException, status
from fastapi.security import (
    OAuth2PasswordBearer,
    SecurityScopes
)

from api.repository.repository import connect
from api.model.PH_Main import user, token, tokenData

load_dotenv()
db = connect()

ALGORITHM = str(os.environ['ALGORITHM'])
SECRET_KEY = str(os.environ['SECRET_KEY_JWT'])
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ['ACCESS_TOKEN_EXPIRE_MINUTES'])

user_collection = db['user']
token_collection = db['token']
token_data_collection = db['tokenData']

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl='api/v1/login',
    scopes={
        'me': 'Read or update current user profile',
        'users': 'Read list of registered user',
        'logout': 'User logout',
        'app-admin': 'Delete community'
    }
)
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


async def is_field_exist(username: Optional[str] = None, email: Optional[str] = None, ui_identity_number: Optional[str] = None):
    if username and email and ui_identity_number:
        user = await user_collection.find_one({
            '$or': [
                {'username': username},
                {'email': email},
                {'uiIdentityNumber': ui_identity_number}
            ]
        })
        return user


async def insert_item(user: Optional[user.User] = None, token: Optional[token.Token] = None, token_data: Optional[tokenData.TokenData] = None):
    if user:
        user['password'] = get_password_hash(user['password'])
        return await user_collection.insert_one(user)
    if token:
        return await token_collection.insert_one(token)
    if token_data:
        return await token_data_collection.insert_one(token_data)


async def get_all_item(skip: int = 0, limit: int = 10):
    return await user_collection.find(skip=skip, limit=limit).to_list(1000)

async def get_specific_user_by_email(user_email: str):
    return await user_collection.find_one({'email': user_email})

async def get_specific_item(username: Optional[str] = None, token_data: Optional[tokenData.TokenData] = None):
    if username:
        return await user_collection.find_one({'username': username})
    if token_data:
        return await token_data_collection.find_one({'username': token_data})


async def update_item(data: dict, id: Optional[str] = None):
    user = await user_collection.find_one({'_id': id})
    if user:
        return await user_collection.update_one({"_id": id}, {"$set": data})


async def delete_user_token(token: str):
    if token:
        return await token_collection.delete_one({'access_token': token})


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(security_scopes: SecurityScopes, token: str = Depends(oauth2_scheme)):
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = f'Bearer'
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': authenticate_value}
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        if username is None:
            raise credentials_exception
        token_scopes = payload.get('scopes', [])
        token_data = tokenData.TokenData(
            username=username,
            scopes=token_scopes
        )
        check_before_insert = await get_specific_item(token_data=token_data.username)
        if not check_before_insert:
            await insert_item(token_data=jsonable_encoder(token_data))
    except (JWTError, ValidationError):
        raise credentials_exception

    valid_token_data = await get_specific_item(token_data=token_data.username)
    user = await get_specific_item(username=valid_token_data['username'])
    if user is None:
        raise credentials_exception
    for scope in security_scopes.scopes:
        if scope not in valid_token_data['scopes']:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Not enough permissions',
                headers={'WWW-Authenticate': authenticate_value}
            )
    return {
        'user': user,
        'token': token
    }

