FROM python:3.8.5-slim-buster

ENV PIP_NO_CACHE_DIR 1

RUN sed -i.bak 's/us-west-2\.ec2\.//' /etc/apt/sources.list

# Installing Required Packages
RUN apt update && apt upgrade -y && \
    apt install --no-install-recommends -y 
    python3-lxml \
    postgresql \
    postgresql-client \
    python3-psycopg2 \
    python3-pip \
    python3-requests \
    python3-sqlalchemy \
    python3-tz \
    python3-aiohttp \
    openssl \
    python3 \
    python3-dev \
    sudo \
    && rm -rf /var/lib/apt/lists /var/cache/apt/archives /tmp

# Pypi package Repo upgrade
# RUN pip3 install --upgrade pip setuptools

RUN git clone https://github.com/error-corpse/TELEGRAM-BOT/ /root/AuctionBot
WORKDIR /root/AuctionBot


ENV PATH="/home/bot/bin:$PATH"

# Install requirements
RUN pip3 install -U -r requirements.txt

# Starting Worker
CMD ["python3","-m","AuctionBot"]
