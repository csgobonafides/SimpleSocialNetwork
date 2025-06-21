FROM python:3.9.2-slim-buster

WORKDIR /service_authentication

ENV TZ 'UTC'
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=
ENV POETRY_HOME=/opt/poetry
ENV PATH="$POETRY_HOME/bin:$PATH"

RUN apt update \
    && apt install -y gcc bash curl\
    && pip install --upgrade pip

RUN curl -sSL https://install.python-poetry.org | python3 - \
    && cd /usr/local/bin \
    && ln -s /root/.local/bin/poetry \
    && poetry config virtualenvs.create false

RUN poetry --version

COPY pyproject.toml poetry.lock* ./

RUN poetry install --no-root --no-dev

COPY ./src .

CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--log-config", "core/logging.yaml"]
