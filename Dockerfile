FROM python:3.12-slim

WORKDIR /app
COPY . ./

# System Prerequistes
RUN apt-get update

# System Depedencies
RUN apt-get install -y --no-install-recommends \
  gettext \
  vim \
  && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set logo path as build argument and environment variable
ARG LOGO_PATH=../static/img/logo.png
ENV LOGO_PATH=${LOGO_PATH}

CMD ["python", "-u", "main.py"]
