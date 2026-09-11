from datetime import datetime, timedelta
from pathlib import Path
from typing import Annotated
from fastapi import APIRouter, Depends, Form, HTTPException, Response, Cookie, UploadFile, File
from pydantic import BaseModel, EmailStr, Field, field_validator
from sqlalchemy import select
from sqlalchemy.orm import session
from sqlalchemy.exc import IntegrityError
from starlette import status
from src.database import AsyncSession, new_session
from src.models.models import User
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
import re
from src.schemas.users import Token, CreateUserRequest
from src.models.models import User
from typing import Optional

import uuid
from PIL import Image
from io import BytesIO

from dotenv import load_dotenv
import os

import hashlib
import secrets

# 1. Сначала загружаем .env
load_dotenv()


router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

SECRET_KEY = os.getenv('JWT_SECRET_KEY')
ALGORITHM = os.getenv('JWT_ALGORITHM')

UPLOAD_DIR = Path("media") / "profile_pics"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 МБ

if not SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY не найден в переменных окружения! Проверьте .env")

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')


async def get_session():
    async with new_session() as session:
        yield session

SessionAuthDep = Annotated[AsyncSession, Depends(get_session)]



@router.post('/create/user', status_code=status.HTTP_201_CREATED)
async def create_user(
    session: SessionAuthDep, 
    # create_user_request: CreateUserRequest,
    file: Optional[UploadFile] = File(None),
    username: str = Form(...),
    email: EmailStr = Form(...),
    password: str = Form(...),
):

    hashed_password = hash_password(password)

    image_filename: Optional[str] = None

    if file:
        contents = await file.read()
        if len(contents) > MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail='Файл слишком большой (максимум 5 мб)'
            )

        try:
            img = Image.open(BytesIO(contents))
            img.verify()
            img = Image.open(BytesIO(contents))

        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Загруженный файл не является валидным изображением'
            )


    # format_to_ext = {"JPEG": "jpg", "PNG": "png", "GIF": "gif", "WEBP": "webp"}
    # ext = format_to_ext.get(img.format, 'jpg')

        image_filename = f'{uuid.uuid4().hex}.jpg'
        file_path = UPLOAD_DIR / image_filename

        with open(file_path, 'wb') as buffer:
            buffer.write(contents)


    create_user_model = User(
        username = username,
        hashed_password = hashed_password,
        email = email,
        image_file=image_filename,
    )

    session.add(create_user_model)

    try: 
        await session.commit() 
        await session.refresh(create_user_model)  # чтобы получить id и другие автополя
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким именем уже существует."
        )

    return {"username": username}


@router.post('/token', response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: SessionAuthDep,
    response: Response):
    user = await authenticate_user(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user')
    token = create_access_token(user.username, user.id, timedelta(minutes=200)) # ‼️‼️ вернуть 20 мин

    # <-- Кладём токен в cookie
    response.set_cookie(
        key='access_token',
        value=token,
        samesite='lax',
        secure=False,    # True, если HTTPS
        max_age=12000,    # 20 минут (как у токена) ‼️‼️ вернуть 20 мин
        path='/'
    )

    print('token:', token)
    return Token(access_token=token, token_type="bearer")





async def authenticate_user(username: str, password: str, session: SessionAuthDep):
    query = select(User).where(User.username == username)
    # 2. Выполняем за прос
    result = await session.execute(query)
    # 3. Получаем одну строку (или None)
    user = result.scalar_one_or_none()


    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user



def hash_password(password: str) -> str:
    hashed_password = bcrypt_context.hash(password)
    return hashed_password

def verify_password(password: str, stored_hash: str) -> bool:
    return bcrypt_context.verify(password, stored_hash)

def create_access_token(username: str, user_id: int, expires_delta: timedelta):
    encode = {'sub': username, 'id': user_id}
    expires = datetime.utcnow() + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM )

def create_reset_token() ->str:
    return secrets.token_urlsafe(32)

def hash_reset_token(token: str) -> str:
    # хэшируем не так, как пароль, тк тот способ хэширования
    # каждый раз возвращает разный результат. А нам надо одинаковый,
    # чтобы сверять хэш полученного токена с записаном хэшем в БД
    return hashlib.sha256(token.encode("utf-8")).hexdigest()

def verify_reset_token(token: str, stored_hash: str) -> bool:
    return bcrypt_context.verify(token, stored_hash)





async def get_current_user(token: Annotated[str, Depends(oauth_bearer)], session: SessionAuthDep):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user')

        user_query = await session.execute(select(User).where(User.id == user_id))
        user = user_query.scalars().first()
        return user

    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user')




async def get_current_user_from_cookie(
    access_token: str | None = Cookie(default=None),
    session: SessionAuthDep = None,
):
    if not access_token:
        return None
        # raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Не авторизован')

    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user')

        user_query = await session.execute(select(User).where(User.id == user_id))
        user = user_query.scalars().first()
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Пользователь не найден')
        return user

    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user')




# @router.post('/log_out', summary='log_out user', tags=['auth'])
# async def log_out_user(session: SessionAuthDep):
#     return Response(content={'messsage': 'Успешный выход из системы. Пожалуйста, удалите токен на клиенте.'})


