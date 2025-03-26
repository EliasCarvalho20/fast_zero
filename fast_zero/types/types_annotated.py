from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.security import get_current_user

T_CurrentUser = Annotated[User, Depends(get_current_user)]
T_OAuthForm = Annotated[OAuth2PasswordRequestForm, Depends()]
T_Session = Annotated[Session, Depends(get_session)]
