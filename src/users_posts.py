from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, Request
from sqlalchemy import func, select

from src.dependences import SessionDep, UserDependency, templates

from src.schemas.posts import PostValidate

from src.models.models import Post, User

from sqlalchemy.orm import selectinload

from src.utils import show_read_more

router = APIRouter(
    prefix='/post',
    tags=['Posts 📝']
)

@router.post('/api/create', summary='Создать пост')
async def create_post(session: SessionDep, post: PostValidate, user: UserDependency):        
    new_post = Post(
        title = post.title,
        content = post.content,
        user_id = user.id,
        date_posted = datetime.now(UTC)
    )

    session.add(new_post)
    await session.commit()
    await session.refresh(new_post)
    return new_post



@router.get('/create_post_form', summary='Отобразить форму для создания поста')
async def create_post_form(request: Request, user: UserDependency):
    if not user:
        raise HTTPException(status_code=400, detail='Пользователь на авторизован')
    return templates.TemplateResponse(request, 'create_post_form.html')



# API
@router.get('/api/show_posts', summary='Показать все посты')
async def api_show_all_posts(
    session: SessionDep, 
    request: Request,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 5,
    ):

    count_query = await session.execute(select(func.count()).select_from(Post))
    total = count_query.scalar() or 0

    query = await session.execute(
        select(Post)
        .options(selectinload(Post.author))
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
        'posts': posts,
        'total': total,
        'skip': skip,
        'limit': limit,
        'has_more': has_more,
    }

    return(output)
    # for test
    # return posts



@router.get('/show_posts', summary='Показать все посты')
async def show_all_posts(
    session: SessionDep, 
    request: Request,
    skip: Annotated[int, Query(ge=0)] = 5,
    limit: Annotated[int, Query(ge=1, le=100)] = 5,
    ):

    count_query = await session.execute(select(func.count()).select_from(Post))
    total = count_query.scalar() or 0

    query = await session.execute(
        select(Post)
        .options(selectinload(Post.author))
        .order_by(Post.date_posted.desc())
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

    has_more = len(posts) < total

    output = {
        'posts': posts,
        'total': total,
        'skip': skip,
        'limit': limit,
        'has_more': has_more,
    }

    return templates.TemplateResponse(request, 'all_posts.html', output)
 
    # for test
    # return posts




@router.get('/show_post/{id}', summary='Показать посты по id')
async def show_all_posts(session: SessionDep, request: Request, id: int):

    query = await session.execute(select(Post).where(Post.id == id).options(selectinload(Post.author)))

    post = query.scalars().first()

    return templates.TemplateResponse(request, 'post_by_id.html', {'post': post})


@router.delete('/delete/post/{id}', summary='Удалить пост по id')
async def delete_post_by_id(session: SessionDep, id: int):

    query = await session.execute(select(Post).where(Post.id == id))

    post = query.scalar_one_or_none()

    if not post:
        raise HTTPException(status_code=404, detail={'message:': 'Пост с таким id не найден'})

    await session.delete(post)
    await session.commit()

    return {'status_code':200, 'detail': {post}}


# API
@router.get('/api/user/{id}/show_posts', summary='Показать все посты пользователя')
async def api_show_user_posts(
    session: SessionDep, 
    request: Request, 
    id: int,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 5,
    ):

    count_query = await session.execute(select(func.count()).select_from(Post).where(Post.user_id == id))
    total = count_query.scalar() or 0

    user_query = await session.execute(select(User).where(User.id == id))
    user = user_query.scalars().first()


    query = await session.execute(
        select(Post).where(Post.user_id == id)
        .options(selectinload(Post.author))
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
        'posts': posts,
        'total': total,
        'skip': skip,
        'limit': limit,
        'has_more': has_more,
        'user': user,
    }

    return output


@router.get('/user/{id}/show_posts', summary='Показать все посты пользователя')
async def show_user_posts(
    session: SessionDep, 
    request: Request, 
    id: int,
    skip: Annotated[int, Query(ge=0)] = 5,
    limit: Annotated[int, Query(ge=1, le=100)] = 5,
    ):

    count_query = await session.execute(select(func.count()).select_from(Post).where(Post.user_id == id))
    total = count_query.scalar() or 0

    user_query = await session.execute(select(User).where(User.id == id))
    user = user_query.scalars().first()


    query = await session.execute(
        select(Post).where(Post.user_id == id)
        .options(selectinload(Post.author))
        .order_by(Post.date_posted.desc())
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

    has_more = len(posts) < total

    output = {
        'posts': posts,
        'total': total,
        'skip': skip,
        'limit': limit,
        'has_more': has_more,
        'user': user,
    }

    return templates.TemplateResponse(request, 'all_user_posts.html', output)


@router.patch('/{id}/edit', summary='Редактировать пост')
async def edit_post(
    id: int,
    update_info: PostValidate,
    session: SessionDep
):
    current_post_query = await session.execute(select(Post).where(Post.id == id))
    current_post = current_post_query.scalars().first()

    update_title = update_info.title
    update_content = update_info.content


    if update_title is not None and update_title != current_post.title:
        current_post.title = update_title  

    if update_content is not None and update_content != current_post.content:
        current_post.content = update_content  


    await session.commit()
    await session.refresh(current_post)

    return current_post



@router.get('/{id}/edit', summary='Форма редактирования поста')
async def show_edit_post_form(
    id: int,
    session: SessionDep,
    request: Request
):
    query= await session.execute(select(Post).where(Post.id == id))
    post = query.scalars().first()

    return templates.TemplateResponse(request, 'edit_post.html', {'post': post})
