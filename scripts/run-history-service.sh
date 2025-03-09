#!/bin/bash

root=/home/pmhalvor
tokenpath=/radio/.token
datapath=/data
docker pull  ghcr.io/pmhalvor/radio_history:latest
docker run --rm --env-file .env -v ${root}${tokenpath}:${tokenpath} -v ${root}${datapath}:${datapath}  ghcr.io/pmhalvor/radio_history:latest
