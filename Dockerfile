FROM python:3.6-alpine AS build-image

ENV PYTHONDONTWRITEBYTECODE 1
ENV TERM xterm-256color

WORKDIR /prunetags

COPY . /prunetags/

RUN apk add --update --no-cache git gcc libc-dev libffi-dev openssl-dev
RUN pip install pybuilder==0.11.17
RUN pyb install_dependencies
RUN pyb
RUN pyb publish


FROM python:3.6-alpine

ENV PYTHONDONTWRITEBYTECODE 1
ENV TERM xterm-256color

WORKDIR /opt/prunetags

COPY --from=build-image /prunetags/target/dist/prunetags-*/dist/prunetags-*.tar.gz /opt/prunetags

RUN apk add --update --no-cache git gcc libc-dev libffi-dev openssl-dev
RUN pip install git+https://github.com/soda480/github3api.git@master#egg=github3api

RUN pip install prunetags-*.tar.gz

CMD echo 'DONE'
