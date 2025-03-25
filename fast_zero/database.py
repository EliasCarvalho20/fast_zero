from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from fast_zero.settings import Settings

engine = create_engine(Settings().DATABASE_URL)


def get_session() -> Generator[Session, None]:  # pragma: no cover
    with Session(engine) as session:
        yield session
