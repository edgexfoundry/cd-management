FROM python:3.6.5-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV TERM xterm-256color

RUN mkdir /githubsync

COPY . /githubsync/

WORKDIR /githubsync

RUN apt-get update
RUN apt-get install -y git gcc libssl-dev

RUN pip install pybuilder==0.11.17
RUN pyb clean
RUN pyb install_dependencies
RUN pyb -X
RUN pyb install

WORKDIR /githubsync
CMD echo 'DONE'
