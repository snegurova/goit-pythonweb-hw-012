FROM python:3.12-slim

ENV POETRY_VERSION=1.8.2
RUN pip install "poetry==$POETRY_VERSION"

WORKDIR /app

COPY pyproject.toml poetry.lock* /app/

RUN poetry config virtualenvs.create false \
  && poetry install --no-root

COPY . /app

EXPOSE 8080

CMD ["bash", "-c", "alembic upgrade head && poetry run uvicorn main:app --host 0.0.0.0 --port 8000 --reload"]