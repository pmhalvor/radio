#!/bin/bash

user=pmhalvor

# Note: volume mounts are case sensitive!
root=/home/${user}
tokenpath=/radio/.token
datapath=/data

docker pull  ghcr.io/${user}/radio_history:latest

docker run --rm --env-file ${root}/radio/.env -v ${root}${tokenpath}:${tokenpath} -v ${root}${datapath}:${datapath}  ghcr.io/${user}/radio_history:latest
