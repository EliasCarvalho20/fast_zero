from http import HTTPStatus

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from fast_zero.models import User
from fast_zero.schemas import Token
from fast_zero.security import create_acess_token, verify_password
from fast_zero.types.types_annotated import T_OAuthForm, T_Session

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token", response_model=Token)
def login_for_acess_token(
    form_data: T_OAuthForm,
    session: T_Session,
) -> dict[str, str]:
    user = session.scalar(select(User).where(User.email == form_data.username))

    if user is None or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    access_token = create_acess_token(data_payload={"sub": user.email})

    return {"access_token": access_token, "token_type": "Bearer"}
