FROM python:3.12-slim

RUN pip install --upgrade pip && pip install poetry

WORKDIR /app

COPY pyproject.toml poetry.lock* /app/

RUN poetry config virtualenvs.create false \
  && poetry install --no-root

COPY . /app

CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]