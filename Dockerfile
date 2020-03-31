FROM python:3.8-slim-buster
MAINTAINER Viacheslav Alferov <psijic@gmail.com>

RUN apt-get update
#RUN apt-get -y upgrade
RUN apt-get -y install ffmpeg

#RUN pip3 install --upgrade pip
RUN pip3 --no-cache install flask
RUN pip3 --no-cache install sqlalchemy

RUN apt-get clean

COPY . /app
WORKDIR /app
CMD python3 server.py