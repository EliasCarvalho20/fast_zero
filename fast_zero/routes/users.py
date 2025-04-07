from http import HTTPStatus
from typing import Sequence

from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from fast_zero.models import User
from fast_zero.schemas import Message, UserList, UserPublic, UserSchema
from fast_zero.security import get_password_hash
from fast_zero.types.types_app import T_Session
from fast_zero.types.types_users import T_CurrentUser, T_ReadUsersFilter

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=UserList)
async def read_users(
    session: T_Session, filter_users: T_ReadUsersFilter
) -> dict[str, Sequence[User]]:
    query = await session.scalars(
        select(User).offset(filter_users.offset).limit(filter_users.limit)
    )

    return {"users": query.all()}


@router.post("/", status_code=HTTPStatus.CREATED, response_model=UserPublic)
async def create_user(user: UserSchema, session: T_Session) -> User:
    if db_user := await session.scalar(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    ):
        if db_user.username == user.username:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail="Username already exists",
            )
        if db_user.email == user.email:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT, detail="Email already exists"
            )

    db_user = User(
        username=user.username,
        password=get_password_hash(user.password),
        email=user.email,
    )
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)

    return db_user


@router.put("/{user_id}", response_model=UserPublic)
async def update_users(
    user_id: int,
    user: UserSchema,
    session: T_Session,
    current_user: T_CurrentUser,
) -> User:
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="Not enough permission",
        )

    try:
        current_user.username = user.username
        current_user.email = user.email
        current_user.password = get_password_hash(user.password)

        await session.commit()
        await session.refresh(current_user)

        return current_user

    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail="Username or Email already exists",
        )


@router.delete("/{user_id}", response_model=Message)
async def delete_users(
    user_id: int,
    session: T_Session,
    current_user: T_CurrentUser,
) -> dict[str, str]:
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="Not enough permission",
        )

    await session.delete(current_user)
    await session.commit()

    return {"message": "User deleted successfully"}
