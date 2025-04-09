from factory import (
    Factory,
    Faker,
    LazyAttribute,
    Sequence,
    post_generation,
)
from factory.fuzzy import FuzzyChoice

from fast_zero.models import Todo, TodoState, User
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


class TodoFactory(Factory):
    class Meta:
        model = Todo

    title = Faker("text", max_nb_chars=20)
    description = Faker("sentence", nb_words=30)
    state = FuzzyChoice(TodoState)
    user_id = 1
