from sqlalchemy import select

from fast_zero.models import User


def test_create_user(session):
    username = "test"
    email = "test@test.com"
    password = "test"

    new_user = User(username=username, email=email, password=password)
    session.add(new_user)
    session.commit()

    user = session.scalar(select(User).where(User.email == email))

    assert user.username == username
