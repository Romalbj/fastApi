from io import BytesIO
from typing import Annotated
import uuid

from fastapi import APIRouter, File, Form, HTTPException, Query, Request, UploadFile
from sqlalchemy import func, select

from src.auth import MAX_FILE_SIZE_BYTES, UPLOAD_DIR
from src.models.models import Post, User
from src.dependences import SessionDep, UserDependency
from src.utils import show_read_more
from starlette import status
from PIL import Image
from src.dependences import templates

router = APIRouter(
    prefix='/user',
    tags=['User profile 👤']
)

# API
@router.get('/api/{id}/profile', summary='Профиль пользователя')
async def api_show_user_profile(
    id: int,
    user: UserDependency,
    request: Request,
    session: SessionDep,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 5
    ):
    
    count_query = await session.execute(select(func.count()).select_from(Post).where(Post.user_id == id))
    total = count_query.scalar() or 0

    query = await session.execute(
        select(Post).where(Post.user_id == id)
        .order_by(Post.date_posted.desc())
        .offset(skip)
        .limit(limit)
    )

    result = query.scalars().all()
    

    posts = [
        {
            "post": post,
            "show_read_more": show_read_more(post.content or ""),
        }
        for post in result
    ]

    has_more = skip + len(posts) < total

    output = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'profile_pic': user.image_path,
        'posts': posts,
        'skip': skip,
        'limit': limit,
        'has_more': has_more,
    }


    return output



@router.get('/{id}/profile', summary='Профиль пользователя')
async def show_user_profile(
    id: int,
    user: UserDependency,
    request: Request,
    session: SessionDep,
    skip: Annotated[int, Query(ge=0)] = 5,
    limit: Annotated[int, Query(ge=1, le=100)] = 5,
    ):

    count_query = await session.execute(select(func.count()).select_from(Post).where(Post.user_id == id))
    total = count_query.scalar() or 0

    query = await session.execute(
        select(Post).where(Post.user_id == id)
        .order_by(Post.date_posted.desc())
        .limit(limit)
    )
    
    # user_current = query.scalars().first()
    result = query.scalars().all()

    
    posts = [
        {
            "post": post,
            "show_read_more": show_read_more(post.content or ""),
        }
        for post in result
    ]

    has_more = len(posts) < total

    values_dict = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'profile_pic': user.image_path,
        'posts': posts,
        'total': total,
        'skip': skip,
        'limit': limit,
        'has_more': has_more,
    }



    return templates.TemplateResponse(request, 'profile.html', values_dict)

    

@router.patch('/{id}/profile', summary='Изменить данные профиля')
async def change_user_profile(
    session: SessionDep,
    id: int,
    username_new: str | None = Form(default=None),
    email_new: str | None = Form(default=None),
    delete_photo: str | None = Form(default=None),
    file: UploadFile | None = File(None),

    # user_uodate: UserBase
    
    ):

    # username_new = user_uodate.username
    # email_new = user_uodate.email

    user_current_query = await session.execute(select(User).where(User.id == id))
    user_current = user_current_query.scalars().first()


    if username_new is not None and username_new != user_current.username:
        check_username_query = await session.execute(select(User).where(User.username == username_new))
        existing_user = check_username_query.scalars().first()
        if existing_user:
            raise HTTPException(
                status_code=404,
                detail='user already exist'
            )

        
    if email_new is not None and email_new != user_current.email:
        check_email_query = await session.execute(select(User).where(User.email == email_new))
        existing_user = check_email_query.scalars().first()
        if existing_user:
            raise HTTPException(
                status_code=404,
                detail='user already exist'
            )

    if delete_photo:
        user_current.image_file = '/default.png'
        #  



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


            if user_current.image_file:
                old_path = UPLOAD_DIR / user_current.image_file
                try:
                    old_path.unlink()
                except FileNotFoundError:
                    pass 

            new_filename =  f'{uuid.uuid4().hex}.jpg'
            new_path = UPLOAD_DIR / new_filename

            with open(new_path, 'wb') as f:
                f.write(contents)

            user_current.image_file = new_filename


        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Загруженный файл не является валидным изображением'
            )

    if username_new is not None:
        user_current.username = username_new
    if email_new is not None:
        user_current.email = email_new

    await session.commit()
    await session.refresh(user_current)

    return user_current
