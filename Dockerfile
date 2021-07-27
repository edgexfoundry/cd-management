FROM python:3.6-alpine

ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /prepbadge

COPY . /prepbadge/

RUN apk add git gnupg openssh netcat-openbsd --no-cache
RUN pip install pybuilder==0.11.17
RUN pyb install_dependencies
RUN pyb install
