FROM rasa/rasa:3.5.3-full 

WORKDIR /app
COPY . /app

USER 1001

VOLUME /app
VOLUME /app/models

CMD [ "run","-m","/app/models","--enable-api","--cors","*","--debug", "--endpoints", "endpoints.yml"]