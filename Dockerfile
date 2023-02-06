FROM python:3.9 as base

# Install some packages
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
    vim \
    wget \
    curl \
    apt install tesseract-ocr -y \
    apt-get install git

# Add a non-root user
RUN useradd -ms /bin/bash app
USER app

# Setup some paths
ENV PYTHONPATH=/home/app/.local/lib/python3.8/site-packages:/home/app/src
ENV PATH=$PATH:/home/app/.local/bin

# Install the python packages for this new user
ADD requirements.txt .
RUN pip3 install -r requirements.txt

WORKDIR /home/app