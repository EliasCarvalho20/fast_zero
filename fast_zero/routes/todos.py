from http import HTTPStatus

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from fast_zero.models import Todo
from fast_zero.schemas import (
    Message,
    TodoList,
    TodoPublic,
    TodoSchema,
)
from fast_zero.types.types_app import T_Session, T_TodosFilter, T_TodoUpdate
from fast_zero.types.types_users import T_CurrentUser

router = APIRouter(prefix="/todos", tags=["todos"])


@router.post("/", response_model=TodoPublic)
async def create_todo(
    user: T_CurrentUser, session: T_Session, todo: TodoSchema
):
    db_todo = Todo(
        title=todo.title,
        description=todo.description,
        state=todo.state,
        user_id=user.id,
    )

    session.add(db_todo)
    await session.commit()
    await session.refresh(db_todo)

    return db_todo


@router.get("/{todo_id}", response_model=TodoPublic)
async def get_todo_by_id(
    todo_id: int,
    user: T_CurrentUser,
    session: T_Session,
):
    todo = await session.scalar(
        select(Todo).where(Todo.user_id == user.id, Todo.id == todo_id)
    )

    if todo is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Todo not found",
        )

    return todo


@router.get("/", response_model=TodoList)
async def get_user_todos(
    user: T_CurrentUser,
    session: T_Session,
    todos_filter: T_TodosFilter,
):
    query = (
        select(Todo)
        .where(Todo.user_id == user.id)
        .offset(todos_filter.offset)
        .limit(todos_filter.limit)
    )

    if todos_filter.title:
        query = query.filter(Todo.title.contains(todos_filter.title))

    if todos_filter.description:
        query = query.filter(
            Todo.description.contains(todos_filter.description)
        )

    if todos_filter.state:
        query = query.filter(Todo.state == todos_filter.state)

    all_todos = await session.scalars(query)

    return {"todos": all_todos.all()}


@router.patch("/{todo_id}", response_model=TodoPublic)
async def update_todo(
    todo_id: int, todo: T_TodoUpdate, user: T_CurrentUser, session: T_Session
):
    todo_to_update = await session.scalar(
        select(Todo).where(Todo.user_id == user.id, Todo.id == todo_id)
    )
    if todo_to_update is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Todo not found",
        )

    for key, value in todo.model_dump(exclude_unset=True).items():
        setattr(todo_to_update, key, value)

    await session.commit()
    await session.refresh(todo_to_update)

    return todo_to_update


@router.delete("/{todo_id}", response_model=Message)
async def delete_todo(
    todo_id: int,
    session: T_Session,
    current_user: T_CurrentUser,
) -> HTTPException | dict[str, str]:
    todo_to_delete = await session.scalar(
        select(Todo).where(Todo.user_id == current_user.id, Todo.id == todo_id)
    )
    if todo_to_delete is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Todo not found",
        )

    await session.delete(todo_to_delete)
    await session.commit()

    return {"message": "Todo deleted successfully"}
