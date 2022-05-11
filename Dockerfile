FROM python:3.8-slim AS base

WORKDIR /usr/app

ENV PATH="/venv/bin:$PATH"

RUN python -m venv /venv

COPY Pipfile ./

RUN apt-get update \
    && apt-get install -y ffmpeg \
    && apt-get clean \
    && pip install pipenv \
    && pipenv lock --keep-outdated --dev --requirements > requirements.txt \
    && pip install -r requirements.txt

COPY audiochunker ./audiochunker
COPY tests tests

CMD pytest
