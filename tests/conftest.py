from contextlib import contextmanager
from datetime import datetime

import pytest
import pytest_asyncio
from factory import Factory, LazyAttribute, Sequence, post_generation
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool

from fast_zero.app import app
from fast_zero.database import get_session
from fast_zero.models import User, table_registry
from fast_zero.security import get_password_hash


class UserFactory(Factory):
    class Meta:
        model = User

    username = Sequence(lambda n: f"test_user{n}")
    email = LazyAttribute(lambda obj: f"{obj.username}@test.com")
    password = LazyAttribute(
        lambda obj: get_password_hash(f"{obj.username}@test.com")
    )

    @post_generation
    def clean_password(self, create, extracted, **kwargs):
        if extracted:
            self.clean_password = extracted
        else:
            self.clean_password = f"{self.username}@test.com"


@pytest_asyncio.fixture
def client(session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def session():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.create_all)

    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.drop_all)


@pytest_asyncio.fixture
async def user(session):
    user = UserFactory()
    session.add(user)

    await session.commit()
    await session.refresh(user)

    return user


@pytest_asyncio.fixture
async def another_user(session):
    another_user = UserFactory()
    session.add(another_user)

    await session.commit()
    await session.refresh(another_user)

    return another_user


@pytest_asyncio.fixture
def token(client, user):
    response = client.post(
        "/auth/token",
        data={"username": user.email, "password": user.clean_password},
    )
    return response.json()["access_token"]


@contextmanager
def _mock_db_time(*, model, time=datetime(2025, 1, 1)):
    def fake_time_handler(mapper, connection, target):
        if hasattr(target, "created_at"):
            target.created_at = time
        if hasattr(target, "updated_at"):
            target.updated_at = time

    event.listen(model, "before_insert", fake_time_handler)

    yield time

    event.remove(model, "before_insert", fake_time_handler)


@pytest.fixture
def mock_db_time():
    return _mock_db_time
