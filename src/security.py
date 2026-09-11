from datetime import UTC, datetime, timedelta
from io import BytesIO
from typing import Annotated
import uuid

from fastapi import APIRouter, BackgroundTasks, File, Form, HTTPException, Query, Request, UploadFile
from sqlalchemy import func, select, update

import src.auth as auth
from config import settings
from email_utils import send_password_reset_email
from src.schemas.password_reset import ChangePasswordRequest, ForgotPasswordRequest, ResetPasswordRequest
from src.auth import MAX_FILE_SIZE_BYTES, UPLOAD_DIR, hash_password, verify_password
from src.models.models import PasswordResetToken, Post, User
from src.dependences import SessionDep, UserDependency
from src.utils import show_read_more
from starlette import status
from PIL import Image
from src.dependences import templates
from sqlalchemy import delete as sql_delete

router = APIRouter(
    prefix='/security',
    tags=['Change / reset password 🔐']
)


# API
@router.post('/api/forgot_password', summary='', status_code=status.HTTP_202_ACCEPTED)
async def api_forgot_password(
    background_tasks: BackgroundTasks,
    session: SessionDep,
    # email: EmailStr = Form(...),
    payload: ForgotPasswordRequest,
):

    query = await session.execute(select(User).where(func.lower(User.email) == str(payload.email).lower()))
    user = query.scalars().first()

    if not user:
        return {"detail": "Если пользователь с таким email существует, письмо отправлено"}
        # raise HTTPException(
        #     status_code=status.HTTP_400_BAD_REQUEST,
        #     detail='Нет пользователей с таким адресом электронной почты'
        # )
        # return {'message': 'Нет пользователей с таким адресом электронной почты'}
    
    await session.execute(sql_delete(PasswordResetToken).where(PasswordResetToken.user_id == user.id))

    token = auth.create_reset_token()
    token_hash = auth.hash_reset_token(token)
    expires_at = datetime.now(UTC) + timedelta(
        minutes=settings.reset_token_expire_minutes
    )

    reset_token = PasswordResetToken(
        user_id = user.id,
        token_hash = token_hash,
        expires_at = expires_at,
    )

    session.add(reset_token)
    await session.commit()

    background_tasks.add_task(
        send_password_reset_email,
        to_email = user.email,
        username = user.username,
        token = token,
    )

    return {'message': 'Все четенько, родной', 'token': reset_token}

# API
@router.post('/api/reset_password', summary='', status_code=status.HTTP_200_OK)
async def api_reset_password(
    request_data: ResetPasswordRequest,
    session: SessionDep
):

    token_hash = auth.hash_reset_token(request_data.token)

    token_query = await session.execute(select(PasswordResetToken).where(PasswordResetToken.token_hash == token_hash))
    reset_token = token_query.scalars().first()

    if not reset_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Неверный или просроченный токен'
        ) 

    if reset_token.expires_at < datetime.now(UTC):
        await session.delete(reset_token)
        await session.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Неверный или просроченный токен'
        ) 

    user_query = await session.execute(select(User).where(User.id == reset_token.user_id))
    user = user_query.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Неверный или просроченный токен'
        ) 

    user.hashed_password = auth.hash_password(request_data.new_password)

    await session.execute(
        sql_delete(PasswordResetToken).where(PasswordResetToken.user_id == user.id)
    )

    await session.commit()
    return {'message': 'Пароль успешно изменен'}


@router.get('/email-reset-password', summary='Почта для сброса пароля')
async def email_reset_password(
    request: Request
):
    return templates.TemplateResponse(request, 'email/email_for_reset_password.html')



# API
@router.patch('/api/change-password', summary='Сменить пароль')
async def api_change_password(
    password_data: ChangePasswordRequest,
    current_user: UserDependency,
    session: SessionDep
):
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Неверный пароль'
        )

    if password_data.current_password == password_data.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Пароли совпадают'
        )

    # current_user.hashed_password = hash_password(password_data.new_password)
    new_hashed_password = hash_password(password_data.new_password)

    await session.execute(
        update(User)
        .where(User.id == current_user.id)
        .values(hashed_password=new_hashed_password)
    )

    await session.execute(
        sql_delete(PasswordResetToken).where(PasswordResetToken.user_id == current_user.id)
    )

    await session.commit()
    # await session.refresh(current_user)
    return {'message': '✅ Пароль успешно изменен',}


@router.get('/change-password/form', summary='Форма смены пароля')
async def change_password_form(
    request: Request
):
    return templates.TemplateResponse(request, 'change_password.html')


@router.get('/reset-password', summary='Форма сброса пароля')
async def reset_password_form(
    request: Request
):
    return templates.TemplateResponse(request, 'email/reset_password.html')

