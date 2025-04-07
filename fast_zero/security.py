from datetime import datetime, timedelta
from http import HTTPStatus
from zoneinfo import ZoneInfo

from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import decode, encode
from jwt.exceptions import DecodeError, ExpiredSignatureError
from pwdlib import PasswordHash
from sqlalchemy import select

from fast_zero.models import User
from fast_zero.settings import Settings
from fast_zero.types.types_app import T_OAuthPassBearer, T_Session

pwd_context = PasswordHash.recommended()
oauth2_schema = OAuth2PasswordBearer(tokenUrl="auth/token")

ACCESS_TOKEN_EXPIRE_MINUTES = Settings().ACCESS_TOKEN_EXPIRE_MINUTES
ALGORITHM = Settings().ALGORITHM
SECRET_KEY = Settings().SECRET_KEY


async def get_current_user(session: T_Session, token: T_OAuthPassBearer):
    credentials_exception = HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        subject_email: str = payload.get("sub")
        if subject_email is None:
            raise credentials_exception
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except DecodeError:
        raise credentials_exception

    user = await session.scalar(
        select(User).where(User.email == subject_email)
    )

    if user is None:
        raise credentials_exception

    return user


def get_password_hash(password: str) -> str:
    """
    Hashes a password using the recommended hashing algorithm.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain password against a hashed password.
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_acess_token(data_payload: dict):
    to_encode = data_payload.copy()
    to_encode.update(
        {
            "exp": datetime.now(tz=ZoneInfo("UTC"))
            + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        }
    )

    return encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
