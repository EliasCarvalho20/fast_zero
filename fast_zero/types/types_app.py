from typing import Annotated

from fastapi import Depends, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from fast_zero.database import get_session
from fast_zero.schemas import PaginationFilter, TodosFilter, TodoUpdate

T_PaginationFilter = Annotated[PaginationFilter, Query()]
T_TodosFilter = Annotated[TodosFilter, Query()]
T_TodoUpdate = Annotated[TodoUpdate, Query()]

T_OAuthForm = Annotated[OAuth2PasswordRequestForm, Depends()]
T_OAuthPassBearer = Annotated[
    OAuth2PasswordBearer(tokenUrl="auth/token"), Depends()
]
T_Session = Annotated[AsyncSession, Depends(get_session)]
