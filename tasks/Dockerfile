# Use a minimal base image
FROM python:3.8-slim

# Add your requirements first, so that we can install requirements first
# Requirements are not going to change very often in comparison to code
# so, better to cache this statement and all dependencies in this layer.

# Install dependencies

COPY requirements.txt /
RUN pip install --no-cache-dir -q -r /requirements.txt
RUN apt-get update && apt-get install -y iputils-ping

# Creating working directory. Here we will add the code.
COPY . /tasks
WORKDIR /tasks

ENV PYTHONPATH=/tasks