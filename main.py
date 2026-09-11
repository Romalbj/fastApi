from datetime import UTC, datetime, timedelta
import os
from typing import Annotated

from fastapi.templating import Jinja2Templates

from fastapi import FastAPI, File, Form, HTTPException, Request, Depends, Path, Query, Cookie, UploadFile
import uvicorn
from pydantic import BaseModel, EmailStr, Field, ConfigDict

from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response, FileResponse, RedirectResponse, PlainTextResponse

from fastapi import BackgroundTasks

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, selectinload
from sqlalchemy import select, func, update
from sqlalchemy import delete as sql_delete

from fastapi.staticfiles import StaticFiles
from databases import Database

from src.schemas.posts import PostValidate, PaginatedPostResponse
from src.schemas.users import UserBase
from src.schemas.password_reset import ChangePasswordRequest, ResetPasswordRequest, ForgotPasswordRequest
from src.dependences import SessionDep, UserDependency, templates
from src.models.models import BookModel, Base, PasswordResetToken, Post, User
from src.database import engine, get_session, new_session
from src.schemas.books import NewBookChema
import src.auth as auth
import src.users_posts as users_posts
from src.auth import MAX_FILE_SIZE_BYTES, UPLOAD_DIR, get_current_user, hash_password, verify_password
from src.utils import show_read_more

import src.api_books as api_books
import src.auth_pages as auth_pages
import src.users_posts as users_posts
import src.user_profile as user_profile
import src.security as security

from starlette import status
import time
import asyncio

import uuid
from PIL import Image
from io import BytesIO

from email_utils import send_password_reset_email

from config import settings


# postgres user:   test_fastApi WITH PASSWORD 'fastApi_test_admin' 

app = FastAPI()
app.include_router(auth.router)
app.include_router(users_posts.router)
app.include_router(api_books.router)
app.include_router(auth_pages.router)
app.include_router(auth_pages.router)
app.include_router(users_posts.router)
app.include_router(user_profile.router)
app.include_router(security.router)

app.mount('/static', StaticFiles(directory='static', html=True))
app.mount('/media', StaticFiles(directory='media'),  name='media')


templates = Jinja2Templates(directory="static/templates")



@app.post('/setup_db', tags=['Database'], summary='Настройка базы данных')
async def setupDb():
     async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

        return {'status': 'success'}


# Возвращаем html шаблон
@app.get('/', summary='Главная страница', tags=['Главная'])
def home(request: Request, user: UserDependency):
    return templates.TemplateResponse(request, 'home.html', {'user': user})
    # return FileResponse('static/templates/index.html')



# Чтобы скачать файл используем класс FileResponse с параметром media_type='application/octet-stream',
# filename - имя файла, с которым он скачается у пользователя
@app.get('/download_html', summary='Скачать файл html', tags=['Главная'])
async def download_html():
    return FileResponse(
        path='static/index.html',
        status_code=200,
        filename='some_file.html',
        media_type='application/octet-stream',
    )




#  Кастомное сообщение об ошибке валидации 
# @app.exception_handler(RequestValidationError)
# async def validation_exception_handler(request: Request, exc: RequestValidationError):
#     errors_list = exc.errors()

#     first_error_msg = (
#         errors_list[0]["msg"] 
#         if errors_list 
#         else "Ошибка валидации данных"
#     )

#     # errors_map = {
#     #     'Input should be greater than 0': 'id книги должен быть больше 0',
#     #     'Input should be a valid string': 'Параметр должен быть строкой',
#     # }

#     # first_error_msg = errors[0]["msg"] if errors else "Ошибка валидации данных"

#     return JSONResponse(
#         status_code=422,
#         content={
#             "message": first_error_msg,
#             "details": first_error_msg,
#         },
#     )


# redirect test
@app.get('/old_redirect', tags=['redirect'])
async def old_url():
    return RedirectResponse('/new_redirect')

@app.get('/new_redirect', tags=['redirect'])
async def new_url():
    return PlainTextResponse('Новая страница')









    







# async bcg tasks tests
def sync_task():
    time.sleep(3)
    print('Дождались синхронно')

async def async_task():
    await asyncio.sleep(3 )
    print('Дождались асинхронно')
    


@app.get('/test_async', summary='Запускаем асинхронную функцию в фоне', tags=['Async test'])
async def async_bg_test():

    asyncio.create_task(async_task())
    # await async_task()
    return {'ok': True}


@app.get('/test_sync', summary='Запускаем синхронную функцию в фоне', tags=['Async test'])
async def sync_bg_test(bg_tasks: BackgroundTasks):

    bg_tasks.add_task(sync_task)
    return {'ok': True}





# test fastapi Form obj
@app.get('/test_form', summary='get test form', tags=['test FastApi Form() object'])
async def get_test_form():
    return FileResponse('static/templates/test_form.html')


@app.post('/test_form', summary='post test form', tags=['test FastApi Form() object'])
async def test_form(username: str = Form(...), userage: int = Form(...)):

    print('username: ', username, 'userage: ', userage)
    return {'username': username, 'userage': userage}


if __name__ == '__main__':
    uvicorn.run('main:app', reload=True)