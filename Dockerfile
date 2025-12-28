FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONBUFFERED=1
ENV PYTHONPATH="/app/src"

WORKDIR /app

RUN pip install --no-cache-dir poetry

COPY ./pyproject.toml ./poetry.lock ./

RUN poetry config virtualenvs.create false && poetry install --no-root --only main

COPY ./src ./src

ENTRYPOINT [ "python3", "-m", "shell_check.main" ]