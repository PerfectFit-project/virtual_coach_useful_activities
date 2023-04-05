FROM rasa/rasa:3.2.8-full 

WORKDIR /app
COPY . /app

USER 1001

VOLUME /app
VOLUME /app/models

CMD [ "run","-m","/app/models","--enable-api","--cors","*","--debug", "--endpoints", "endpoints.yml"]