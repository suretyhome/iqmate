FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    iproute2 \
    net-tools \
    nmap \
    nano \ 
    python3 \
    python3-pip \
    nodejs \
    npm \
    mosquitto \
    mosquitto-clients

RUN pip install appdaemon

COPY etc/iqmate /etc/iqmate
COPY bin/* /bin/
