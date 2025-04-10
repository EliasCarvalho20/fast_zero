#!/bin/sh

# Execute database migrations
poetry run alembic upgrade head

# Run the application
poetry run uvicorn --host 0.0.0.0 --port 8000 fast_zero.app:app
