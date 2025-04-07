from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from fast_zero.database import get_session

T_OAuthForm = Annotated[OAuth2PasswordRequestForm, Depends()]
T_OAuthPassBearer = Annotated[
    OAuth2PasswordBearer(tokenUrl="auth/token"), Depends()
]
T_Session = Annotated[AsyncSession, Depends(get_session)]
