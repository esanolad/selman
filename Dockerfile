# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .


ENV TWITTER_CONSUMER_KEY=$
ENV TWITTER_CONSUMER_SECRET=$
ENV TWITTER_ACCESS_TOKEN=$
ENV TWITTER_ACCESS_TOKEN_SECRET=$
ENV TWITTER_BEARER_TOKEN=$
ENV CLIENT_ID=$
ENV CLIENT_SECRET=$
ENV WHATSAPP_BEARER_TOKEN=$
ENV LOG_SERVER=$
ENV LOG_INDEX=$


CMD [ "python3", "main.py"]



