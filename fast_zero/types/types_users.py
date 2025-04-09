from typing import Annotated

from fastapi import Depends

from fast_zero.models import User
from fast_zero.security import get_current_user

T_CurrentUser = Annotated[User, Depends(get_current_user)]
