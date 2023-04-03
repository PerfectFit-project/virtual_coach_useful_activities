FROM rasa/rasa:3.5.3-full 

WORKDIR /app
COPY . /app

USER root

COPY requirements.txt .
RUN pip install -r requirements.txt

# Spacy language model
RUN python -m spacy download en_core_web_lg

USER 1001

VOLUME /app
VOLUME /app/models

CMD [ "run","-m","/app/models","--enable-api","--cors","*","--debug", "--endpoints", "endpoints.yml"]