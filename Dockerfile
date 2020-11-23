FROM python:3.6-alpine AS build-image

ENV PYTHONDONTWRITEBYTECODE 1
ENV TERM xterm-256color

WORKDIR /synclabels

COPY . /synclabels/

RUN apk add --update --no-cache git gcc libc-dev libffi-dev openssl-dev

RUN pip install pybuilder==0.11.17
RUN pyb install_dependencies
RUN pyb install


FROM python:3.6-alpine

ENV PYTHONDONTWRITEBYTECODE 1
ENV TERM xterm-256color

WORKDIR /opt/synclabels

COPY --from=build-image /synclabels/target/dist/synclabels-*/dist/synclabels-*.tar.gz /opt/synclabels

RUN pip install synclabels-*.tar.gz

CMD echo 'DONE'