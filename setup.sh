#!/bin/bash

# update the package manager
apt update -yqq  

# install docker
apt install docker.io -yq 

sudo chmod 777 /var/run/docker.sock

# install the latest version of Astro Cli
curl -sSL install.astronomer.io | sudo bash -s

# create an Astro project
mkdir airflow_pipeline && \
    cd airflow_pipeline && \
    airflow dev init

# run airflow locally
astro dev start
