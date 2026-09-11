FROM python:3.14-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src

RUN pip install --no-cache-dir poetry==2.4.1

RUN poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock ./

RUN poetry install --only main --no-root --no-interaction --no-ansi

COPY src ./src

CMD ["python", "-m", "protogen_delta.main"]