#!/bin/bash

# change to your own user
user=pmhalvor

cd /home/${user}/radio/
docker build -t ghcr.io/${user}/radio_history:latest -f Dockerfile.history .