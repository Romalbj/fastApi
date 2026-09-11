from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from src.dependences import templates


router = APIRouter(
    prefix='/user',
    tags=['User_auth_pages 🔑']
)


# @router.get('/log_in', summary='login user', tags=['User'])
# async def user(user: UserDependency, session: SessionDep):
#     if user is None:
#         raise HTTPException(status_code=401, detail='user not found')
#     return {'user': user}


@router.get('/sign_up_page', summary='Форма создания пользователя')
async def sign_up_page(request: Request):
    return templates.TemplateResponse(request, 'sign_up.html')
    # return FileResponse('static/templates/sign_up.html')


@router.get('/sign_up/success', summary='Успешная регистрация')
async def sign_up_success(request: Request):
    return templates.TemplateResponse(request, 'success_sign_up.html')
    # return FileResponse('static/templates/success_sign_up.html')


@router.get('/log_in_page', summary='Форма авторизации пользователя')
async def log_in_page(request: Request):
    return templates.TemplateResponse(request, 'log_in.html')
    # return FileResponse('static/templates/log_in.html')


@router.get('/log_in/success', summary='Успешная авторизация')
async def log_in_success(request: Request):
    return templates.TemplateResponse(request, 'success_log_in.html')
    # return FileResponse('static/templates/success_log_in.html')