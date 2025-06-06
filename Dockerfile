FROM ubuntu:22.04

# docker build -t oras-py .

LABEL MAINTAINER @vsoch
ENV PATH /opt/conda/bin:${PATH}
ENV LANG C.UTF-8
RUN apt-get update && \
    apt-get install -y wget docker.io && \
    wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh && \
    bash Miniconda3-latest-Linux-x86_64.sh -b -p /opt/conda && \
    rm Miniconda3-latest-Linux-x86_64.sh

RUN pip install ipython pytest requests
WORKDIR /app
COPY . /app
RUN pip install -e .[all]
