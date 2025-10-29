#!/bin/bash

# check for root privileges
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 
   exit 1
fi

echo "Installing Docker..."
sudo zypper install -y docker docker-compose docker-compose-switch

sudo systemctl enable docker
sudo systemctl start docker

sudo usermod -aG docker $USER
# newgrp docker

sudo systemctl restart docker

echo "Starting Docker containers..."
sudo docker-compose up -d
sudo docker ps

echo "Docker containers are now up and running."