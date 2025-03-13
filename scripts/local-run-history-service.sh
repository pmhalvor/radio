#!/bin/bash

user=pmhalvor

# Note: volume mounts are case sensitive!
root=/home/${user}
tokenpath=/radio/.token
datapath=/data

echo "Pull latest version from registry? (y/[n]): "
read answer
if [[ $answer == "y" ]]; then
    docker pull  ghcr.io/${user}/radio_history:latest
else
    echo "Using local latest version."
    echo $(docker images | grep ghcr.io/${user}/radio_history | awk '{print $3}')
fi

docker run --rm --env-file ${root}/radio/.env -v ${root}${tokenpath}:${tokenpath} -v ${root}${datapath}:${datapath}  ghcr.io/${user}/radio_history:latest
