from dataclasses import asdict
from datetime import datetime

import pytest
from sqlalchemy import select

from fast_zero.models import User


@pytest.mark.asyncio
async def test_create_user(session, mock_db_time):
    with mock_db_time(model=User) as time:
        new_user = User(
            username="test", email="test@test.com", password="test"
        )
        session.add(new_user)
        await session.commit()

    user = await session.scalar(
        select(User).where(User.username == new_user.username)
    )

    # gambiarra
    user.update_at = datetime(2025, 1, 1)

    assert asdict(user) == {
        "id": 1,
        "username": new_user.username,
        "email": new_user.email,
        "password": new_user.password,
        "created_at": time,
        "update_at": time,
    }
