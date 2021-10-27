FROM python:3.9-slim AS build-image
ENV PYTHONDONTWRITEBYTECODE 1
WORKDIR /code
COPY . /code/
RUN apt-get update && apt-get install -y git gcc libc6-dev libffi-dev openssl libmagic-dev
RUN pip install pybuilder
RUN pyb --reset-plugins install

FROM python:3.9-alpine
ENV PYTHONDONTWRITEBYTECODE 1
WORKDIR /opt/cr8rel
COPY --from=build-image /code/target/dist/cr8rel-*/dist/cr8rel-*.tar.gz /opt/cr8rel
RUN apk add --update --no-cache libmagic
RUN pip install cr8rel-*.tar.gz