FROM python:3.9-slim AS build-image

ENV PYTHONDONTWRITEBYTECODE 1
ENV TERM xterm-256color

WORKDIR /code
COPY . /code/

RUN pip install pybuilder && \
    pyb --reset-plugins install -vX

FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV TERM xterm-256color

WORKDIR /opt/dockerhub-audit

COPY --from=build-image /code/target/dist/dockerhub-audit-*/dist/dockerhub-audit-*.tar.gz /opt/dockerhub-audit

RUN pip install dockerhub-audit-*.tar.gz
