#!/bin/bash

# change to your own user
user=pmhalvor

cd /home/${user}/radio/
docker build -t ghcr.io/${user}/radio_history:latest -f Dockerfile.history .  --platform linux/amd64

echo "Do you want to push the latest version to the container registry? (y/[n]): "
read answer
if [[ $answer == "y" ]]; then
    docker push ghcr.io/${user}/radio_history:latest
else
    echo "Skipping push to container registry."
fi