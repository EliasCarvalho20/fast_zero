from http import HTTPStatus
from typing import Sequence

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.schemas import Message, Token, UserList, UserPublic, UserSchema
from fast_zero.security import (
    create_acess_token,
    get_current_user,
    get_password_hash,
    verify_password,
)

app = FastAPI()


@app.get("/", response_model=Message)
def read_root() -> dict[str, str]:
    return {"message": "Hello World!"}


@app.post("/token", response_model=Token)
def login_for_acess_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
) -> dict[str, str]:
    """
    Login for access token.

    Args:
        form_data (OAuth2PasswordRequestForm): The form data containing username and password.
        session (Session): The database session.

    Returns:
        dict[str, str]: A dictionary containing the access token and token type.
    """

    user = session.scalar(select(User).where(User.email == form_data.username))

    if user is None or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    access_token = create_acess_token(data_payload={"sub": user.email})

    return {"access_token": access_token, "token_type": "Bearer"}


@app.post("/users", status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(
    user: UserSchema, session: Session = Depends(get_session)
) -> User:
    """
    Create a new user.

    Args:
        user (UserSchema): The user data to create.
        session (Session): The database session.

    Returns:
        User: The created user.

    Raises:
        HTTPException: If the username or email already exists.
    """
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


@app.get("/users", response_model=UserList)
def read_users(
    offset: int = 0, limit: int = 100, session: Session = Depends(get_session)
) -> dict[str, Sequence[User]]:
    """
    Retrieve a list of users with pagination.

    Args:
        offset (int): The number of items to skip before starting to collect the result set. Default is 0.
        limit (int): The maximum number of items to return. Default is 100.
        session (Session): The database session.

    Returns:
        dict[str, Sequence[User]]: A dictionary containing a list of users.
    """
    users = session.scalars(select(User).offset(offset).limit(limit)).all()
    return {"users": users}


@app.put("/users/{user_id}", response_model=UserPublic)
def update_users(
    user_id: int,
    user: UserSchema,
    session=Depends(get_session),
    current_user=Depends(get_current_user),
) -> User:
    """
    Update an existing user.

    Args:
        user_id (int): The ID of the user to update.
        user (UserSchema): The new user data.
        session (Session, optional): The database session.

    Returns:
        User: The updated user.

    Raises:
        HTTPException: If the user is not found.
    """
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
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


@app.delete("/users/{user_id}", response_model=Message)
def delete_users(
    user_id: int,
    session=Depends(get_session),
    current_user=Depends(get_current_user),
) -> dict[str, str]:
    """
    Delete an existing user.

    Args:
        user_id (int): The ID of the user to delete.
        response_model (Message): The response model.
        session (Session): The database session.

    Returns:
        dict[str, str]: A dictionary containing a success message.

    Raises:
        HTTPException: If the user is not found.
    """
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Not enough permission",
        )

    session.delete(current_user)
    session.commit()

    return {"message": "User deleted successfully"}
