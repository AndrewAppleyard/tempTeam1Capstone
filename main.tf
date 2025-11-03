terraform {
    required_providers {
    docker = {
        source = "kreuzwerker/docker"
        version = "~> 3.0"
    }
    }
}

provider "docker" {}

# Example for a Docker container as host (for local development) This would be changed to an aws EC2 or Azure VM
resource "docker_container" "docker_host" {
    name  = "docker-compose-host"
    image = "docker:dind" # Docker-in-Docker image
    privileged = true # Required for running Docker inside (gives sudo privileges)
}

resource "null_resource" "deploy_compose" {
    depends_on = [docker_container.docker_host] # Ensure host is ready

    provisioner "local-exec" {
    command = "docker cp ${path.module}/compose.yaml ${docker_container.docker_host.name}:/"
    #source      = "${path.module}/compose.yaml"
    #destination = "/app/compose.yaml"
    connection {
        host = docker_container.docker_host.name
        type = "docker"
    }
}

provisioner "local-exec" {
    command = "docker cp ./ ${docker_container.docker_host.name}:/"
    connection {
        host = docker_container.docker_host.name
        type = "docker" #this would be changed to ssh for azure or aws
        }
    }
}

resource "null_resource" "start_compose" {
    depends_on = [null_resource.deploy_compose]

    provisioner "local-exec" {
        command =  "ls; cd ${docker_container.docker_host.name}/; docker compose -f ./compose.yaml up -d --build; pwd"
        connection {
          host = docker_container.docker_host.name
          type = "docker"

    }
    }
}