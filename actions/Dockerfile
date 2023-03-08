# Pull SDK image as base image
FROM rasa/rasa-sdk:3.2.1

# Use subdirectory as working directory
WORKDIR /app

# Copy actions requirements
COPY requirements-actions.txt ./

# Change to root user to install dependencies
USER root

RUN pip3 install recognizers-text-suite
RUN pip install mysql-connector-python

# Install extra requirements for actions code
RUN pip install -r requirements-actions.txt

# Copy actions folder to working directory
COPY . /app

# Don't use root user to run code
USER 1001