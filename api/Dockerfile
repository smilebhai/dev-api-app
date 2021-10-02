# Use a minimal base image
FROM python:3.7-slim

# Add your requirements first, so that we can install requirements first
# Requirements are not going to change very often in comparison to code
# so, better to cache this statement and all dependencies in this layer.

# Install dependencies

COPY requirements.txt /
RUN pip install --no-cache-dir -q -r /requirements.txt

# Creating working directory. Here we will add the code.
COPY . /api
WORKDIR /api

ENV PYTHONPATH=/api

# Run Gunicorn to serve api requests and reload on change so we can see our
# changes to the code

ENTRYPOINT ["gunicorn","-w","4","--threads","2","-b","0.0.0.0:8000","app:flask_app","--log-level","debug","-t","1200"]
