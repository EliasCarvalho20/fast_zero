from typing import Annotated

from fastapi import Depends, Query

from fast_zero.models import User
from fast_zero.schemas import FilterPage
from fast_zero.security import get_current_user

T_CurrentUser = Annotated[User, Depends(get_current_user)]
T_ReadUsersFilter = Annotated[FilterPage, Query()]
