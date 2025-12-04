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

    ports{
        internal=8080
        external=8080
        ip="0.0.0.0"
        protocol="tcp"
    }
}

resource "null_resource" "deploy_compose" {
    depends_on = [docker_container.docker_host] # Ensure host is ready

    provisioner "local-exec" {
    command = "docker exec ${docker_container.docker_host.name} sh -c 'mkdir -p /app'; docker cp ${path.module}/compose.yaml ${docker_container.docker_host.name}:/app/"
    #source      = "${path.module}/compose.yaml"
    #destination = "/app/compose.yaml"
    connection {
        host = docker_container.docker_host.name
        type = "docker"
    }
}

provisioner "local-exec" {
    command = "docker cp ./ ${docker_container.docker_host.name}:/app"
    }
}


resource "null_resource" "start_compose" {
  depends_on = [null_resource.deploy_compose]

  provisioner "local-exec" {
    command = <<EOT
      echo "Installing Docker Compose inside container..."
      docker exec ${docker_container.docker_host.name} sh -c "apk add --no-cache docker-cli-compose" 

      echo "Starting docker compose services inside container..."
      docker exec ${docker_container.docker_host.name} sh -c "
        cd /app &&
        ls -l &&
        docker compose -f /app/compose.yaml -p advising up -d
        docker compose -p advising down
        docker compose -p advising up -d
      "

      echo "✅ Compose started successfully"
    EOT
  }
}
