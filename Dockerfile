FROM python:3.6.5-alpine AS build-image

ENV PYTHONDONTWRITEBYTECODE 1
ENV TERM xterm-256color

RUN mkdir /dockerhub-audit

COPY . /dockerhub-audit/

WORKDIR /dockerhub-audit

RUN pip install pybuilder==0.11.17
RUN pyb install_dependencies
RUN pyb install


FROM python:3.6.5-alpine

ENV PYTHONDONTWRITEBYTECODE 1
ENV TERM xterm-256color

WORKDIR /opt/dockerhub-audit

COPY --from=build-image /dockerhub-audit/target/dist/dockerhub-audit-*/dist/dockerhub-audit-*.tar.gz /opt/dockerhub-audit

RUN pip install dockerhub-audit-*.tar.gz
