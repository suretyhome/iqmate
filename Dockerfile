FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    iproute2 \
    net-tools \
    iputils-ping \
    nmap \
    curl \
    nano \
    git \
    python3 \
    python3-pip \
    python3-venv \
    mosquitto \
    mosquitto-clients

RUN cd ~ && curl -fsSL https://deb.nodesource.com/setup_23.x -o nodesource_setup.sh && \
    bash nodesource_setup.sh && \
    apt-get install -y nodejs

RUN pip install appdaemon

RUN npm install -g --unsafe-perm node-red \
    node-red-contrib-modbus \
    node-red-contrib-zwave-js

COPY app/etc/iqmate /etc/iqmate
COPY app/bin/* /bin/

EXPOSE 1880 1883

RUN echo iqmate-start >> ~/.bashrc
