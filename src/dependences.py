from typing import Annotated

from fastapi import Depends
from fastapi.templating import Jinja2Templates

from src.database import get_session
from src.auth import get_current_user, get_current_user_from_cookie

from sqlalchemy.ext.asyncio import AsyncSession

SessionDep = Annotated[AsyncSession, Depends(get_session)]
UserDependency = Annotated[dict, Depends(get_current_user_from_cookie)]


templates = Jinja2Templates(directory="static/templates")