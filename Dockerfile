FROM python:3.9-slim AS build-image
ENV PYTHONDONTWRITEBYTECODE 1
ENV TERM xterm-256color
WORKDIR /code
COPY . /code/
RUN pip install pybuilder
RUN pyb --reset-plugins install

FROM python:3.9-alpine
ENV PYTHONDONTWRITEBYTECODE 1
ENV TERM xterm-256color
WORKDIR /opt/synclabels
COPY --from=build-image /code/target/dist/synclabels-*/dist/synclabels-*.tar.gz /opt/synclabels
RUN pip install synclabels-*.tar.gz