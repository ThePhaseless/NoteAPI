FROM python:slim
SHELL [ "bash", "-c" ]
ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    # Poetry's configuration:
    POETRY_NO_INTERACTION=1

ENV PATH="${PATH}:/root/.local/bin"


WORKDIR /app

RUN apt update && apt install -y pipx

RUN pipx install poetry
COPY *.toml ./
RUN poetry install
COPY . .

CMD [ "poetry", "run", "python", "main.py" ]