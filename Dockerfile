FROM python:3.6-alpine AS build-image

ENV PYTHONDONTWRITEBYTECODE 1
ENV TERM xterm-256color

WORKDIR /prunetags

COPY . /prunetags/

RUN apk update
RUN apk add git gcc
RUN pip install --upgrade pip
RUN pip install pybuilder==0.11.17
RUN pyb clean
RUN pyb install_dependencies
RUN pyb -X
RUN pyb publish


FROM python:3.6-alpine

ENV PYTHONDONTWRITEBYTECODE 1
ENV TERM xterm-256color

WORKDIR /opt/prunetags

COPY --from=build-image /prunetags/target/dist/prunetags-*/dist/prunetags-*.tar.gz /opt/prunetags

RUN pip install prunetags-*.tar.gz

CMD echo 'DONE'
