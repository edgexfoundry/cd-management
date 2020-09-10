FROM python:3.6-alpine AS build-image

ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /create-github-release

COPY . /create-github-release/

RUN apk update
RUN apk add git libmagic
RUN pip install --upgrade pip
RUN pip install pybuilder==0.11.17
RUN pyb install_dependencies
RUN pyb
RUN pyb publish

FROM python:3.6-alpine

ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /opt/create-github-release

COPY --from=build-image /create-github-release/target/dist/ghrelease-*/dist/ghrelease-*.tar.gz /opt/create-github-release

# the following lines are necessary because github3api isn't yet published to PyPi
# once it is published then the following lines will be removed
RUN apk add --update --no-cache git gcc libc-dev libffi-dev openssl-dev wget libmagic
RUN pip install git+https://github.com/soda480/github3api.git@master#egg=github3api

RUN pip install ghrelease-*.tar.gz

CMD echo 'DONE'
