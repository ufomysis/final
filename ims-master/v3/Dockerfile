FROM python:3.7.3
RUN mkdir /v3
WORKDIR /v3
# install dependencies
COPY requirements.txt ./
RUN apt-get update
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# copy project
COPY . .
