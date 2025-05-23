from fastapi import FastAPI

from fast_zero.routes import auth, todos, users
from fast_zero.schemas import Message

app = FastAPI()

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(todos.router)


@app.get("/", response_model=Message)
def read_root() -> dict[str, str]:
    return {"message": "Hello World!"}
