#!/bin/bash
set -e

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

sudo docker-compose up -d dirsrv

echo "Waiting for 389 Directory Server to become ready..."
until sudo docker exec uafs_ldap ldapsearch -x -H ldap://localhost:3389 -b "dc=UAFS,dc=COM" >/dev/null 2>&1; do
  echo "Waiting for dirsrv..."
  sleep 5
done


#sudo docker compose down -v
echo "Starting Docker containers..."
sudo docker-compose up -d
sudo docker ps

echo "Docker containers are now up and running."