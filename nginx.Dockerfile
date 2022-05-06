FROM node:lts

WORKDIR /root/js
COPY ./game/js /root/js
RUN yarn install
RUN yarn run buildprod

FROM python:3.9.5-buster

RUN mkdir /root/pytho
WORKDIR /root/pytho
RUN apt-get update
RUN apt-get -y install python-dev build-essential

COPY requirements.txt /root/pytho
RUN pip install -r requirements.txt
COPY . /root/pytho/

COPY --from=0 /root/js/dist /root/pytho/game/js/dist

ARG DJANGO_SECRET_KEY
RUN python3 manage.py collectstatic --noinput

FROM nginx:1.20

COPY --from=1 /root/pytho/static/ /www/static
