from http import HTTPStatus
from typing import Sequence

from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from fast_zero.models import User
from fast_zero.schemas import Message, UserList, UserPublic, UserSchema
from fast_zero.security import get_password_hash
from fast_zero.types.types_annotated import T_CurrentUser, T_Session

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=UserList)
def read_users(
    session: T_Session, offset: int = 0, limit: int = 100
) -> dict[str, Sequence[User]]:
    users = session.scalars(select(User).offset(offset).limit(limit)).all()
    return {"users": users}


@router.post("/", status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema, session: T_Session) -> User:
    if session.scalar(select(User).where(User.username == user.username)):
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail="Username already exists",
        )
    if session.scalar(select(User).where(User.email == user.email)):
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT, detail="Email already exists"
        )

    db_user = User(
        username=user.username,
        password=get_password_hash(user.password),
        email=user.email,
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


@router.put("/{user_id}", response_model=UserPublic)
def update_users(
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

        session.commit()
        session.refresh(current_user)

        return current_user

    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail="Username or Email already exists",
        )


@router.delete("/{user_id}", response_model=Message)
def delete_users(
    user_id: int,
    session: T_Session,
    current_user: T_CurrentUser,
) -> dict[str, str]:
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="Not enough permission",
        )

    session.delete(current_user)
    session.commit()

    return {"message": "User deleted successfully"}
