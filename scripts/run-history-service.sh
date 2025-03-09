#!/bin/bash

root=/home/pmhalvor
tokenpath=/radio/.token
datapath=/data
docker run --rm -v ${root}${tokenpath}:${tokenpath} -v ${datapath}:${datapath}  ghcr.io/pmhalvor/radio_history:latest