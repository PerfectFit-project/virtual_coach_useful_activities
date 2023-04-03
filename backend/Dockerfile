FROM rasa/rasa:3.5.3-full 

WORKDIR /app
COPY . /app
#COPY ./data /app/data

USER root

#RUN  rasa train
#,"-v","$(pwd):/app"

USER 1001

VOLUME /app
#VOLUME /app/data
VOLUME /app/models
#VOLUME /app/actions

CMD [ "run","-m","/app/models","--enable-api","--cors","*","--debug", "--endpoints", "endpoints.yml"]