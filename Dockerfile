FROM python:3.9-slim
ENV PYTHONDONTWRITEBYTECODE 1
WORKDIR /code
COPY . /code/
RUN apt-get update && apt-get install -y git gnupg netcat-openbsd
RUN pip install pybuilder
RUN pyb --reset-plugins install