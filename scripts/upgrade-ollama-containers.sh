#!/bin/bash
# Ollama Docker Container Upgrade Script
# Created: May 4, 2025
# Purpose: Upgrade Ollama Docker containers while preserving configurations
#          and ensuring models point to a shared directory

# Print header
echo "=========================================================="
echo "  Ollama Docker Container Upgrade Script"
echo "=========================================================="
echo

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
  echo "Error: Docker is not running or you don't have permission to use it."
  echo "Please start Docker or check your permissions and try again."
  exit 1
fi

# Function to display usage
usage() {
  echo "Usage: $0 [OPTIONS]"
  echo
  echo "Options:"
  echo "  -h, --help             Display this help message"
  echo "  -c, --check-only       Check current configuration without upgrading"
  echo "  -v, --verify-only      Verify Ollama versions without upgrading"
  echo "  -f, --force            Force upgrade without confirmation"
  echo
  echo "Example:"
  echo "  $0                     Interactive upgrade with confirmation"
  echo "  $0 --force             Upgrade all containers without confirmation"
  echo "  $0 --check-only        Only check current configuration"
}

# Parse command line arguments
CHECK_ONLY=false
VERIFY_ONLY=false
FORCE=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help)
      usage
      exit 0
      ;;
    -c|--check-only)
      CHECK_ONLY=true
      shift
      ;;
    -v|--verify-only)
      VERIFY_ONLY=true
      shift
      ;;
    -f|--force)
      FORCE=true
      shift
      ;;
    *)
      echo "Unknown option: $1"
      usage
      exit 1
      ;;
  esac
done

# Function to check current configuration
check_configuration() {
  echo "Checking current Ollama container configuration..."
  echo

  # Get list of Ollama containers
  CONTAINERS=$(docker ps -a --filter "name=git-ollama" --format "{{.Names}}")
  
  if [ -z "$CONTAINERS" ]; then
    echo "No Ollama containers found."
    exit 1
  fi
  
  echo "Found the following Ollama containers:"
  for CONTAINER in $CONTAINERS; do
    RUNNING=$(docker ps --filter "name=$CONTAINER" --format "{{.Names}}")
    if [ -z "$RUNNING" ]; then
      STATUS="stopped"
    else
      STATUS="running"
    fi
    
    echo "- $CONTAINER ($STATUS)"
  done
  echo
  
  echo "Container details:"
  for CONTAINER in $CONTAINERS; do
    echo "===== $CONTAINER ====="
    echo "Volumes:"
    docker inspect $CONTAINER --format '{{range .Mounts}}{{.Source}} -> {{.Destination}}{{println}}{{end}}' 2>/dev/null || echo "  Container not found"
    
    echo "Port mappings:"
    docker inspect $CONTAINER --format '{{range $p, $conf := .NetworkSettings.Ports}}{{$p}} -> {{range $conf}}{{.HostPort}}{{end}}{{println}}{{end}}' 2>/dev/null || echo "  Container not found"
    
    echo "Environment variables:"
    docker inspect $CONTAINER --format '{{range .Config.Env}}{{if or (contains . "OLLAMA_MODELS") (contains . "OLLAMA_HOST") (contains . "CUDA_VISIBLE_DEVICES")}}{{println .}}{{end}}{{end}}' 2>/dev/null || echo "  Container not found"
    
    RUNNING=$(docker ps --filter "name=$CONTAINER" --format "{{.Names}}")
    if [ -n "$RUNNING" ]; then
      echo "Ollama version:"
      docker exec $CONTAINER ollama --version 2>/dev/null || echo "  Unable to get version"
    fi
    echo
  done
}

# Function to verify Ollama versions
verify_versions() {
  echo "Verifying Ollama versions in containers..."
  echo
  
  # Get list of running Ollama containers
  CONTAINERS=$(docker ps --filter "name=git-ollama" --format "{{.Names}}")
  
  if [ -z "$CONTAINERS" ]; then
    echo "No running Ollama containers found."
    return
  fi
  
  for CONTAINER in $CONTAINERS; do
    echo "===== $CONTAINER ====="
    docker exec $CONTAINER ollama --version 2>/dev/null || echo "  Unable to get version"
    echo "Model path:"
    docker exec $CONTAINER ls -la /root/.ollama/models 2>/dev/null | head -n 1 || echo "  Unable to check model path"
    echo "Models available:"
    docker exec $CONTAINER ollama list 2>/dev/null | head -n 5 || echo "  Unable to list models"
    echo
  done
}

# Check if only verification is requested
if [ "$VERIFY_ONLY" = true ]; then
  verify_versions
  exit 0
fi

# Check current configuration
check_configuration

# Exit if only checking configuration
if [ "$CHECK_ONLY" = true ]; then
  exit 0
fi

# Confirm upgrade
if [ "$FORCE" = false ]; then
  echo -n "Do you want to upgrade these Ollama containers to the latest version? (y/N): "
  read CONFIRM
  if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
    echo "Upgrade cancelled."
    exit 0
  fi
fi

# Pull latest Ollama image
echo "Pulling latest Ollama image..."
docker pull ollama/ollama:latest

# Get latest image ID
LATEST_IMAGE_ID=$(docker images ollama/ollama:latest --format "{{.ID}}")
echo "Latest Ollama image ID: $LATEST_IMAGE_ID"
echo

# Upgrade each container
for CONTAINER in $CONTAINERS; do
  echo "Upgrading $CONTAINER..."
  
  # Get container configuration
  CONFIG_VOLUME=$(docker inspect $CONTAINER --format '{{range .Mounts}}{{if eq .Destination "/root/.ollama"}}{{if eq .Type "volume"}}{{.Name}}{{end}}{{end}}{{end}}' 2>/dev/null)
  MODELS_PATH=$(docker inspect $CONTAINER --format '{{range .Mounts}}{{if eq .Destination "/root/.ollama/models"}}{{if eq .Type "bind"}}{{.Source}}{{end}}{{end}}{{end}}' 2>/dev/null)
  PORT=$(docker inspect $CONTAINER --format '{{range $p, $conf := .NetworkSettings.Ports}}{{if eq $p "11434/tcp"}}{{range $conf}}{{.HostPort}}{{end}}{{end}}{{end}}' 2>/dev/null)
  CUDA_VISIBLE_DEVICES=$(docker inspect $CONTAINER --format '{{range .Config.Env}}{{if eq . "CUDA_VISIBLE_DEVICES"}}{{println .}}{{end}}{{end}}' 2>/dev/null)
  
  # Check if we got all required configuration
  if [ -z "$CONFIG_VOLUME" ] || [ -z "$MODELS_PATH" ] || [ -z "$PORT" ]; then
    echo "  Error: Could not get complete configuration for $CONTAINER. Skipping."
    continue
  fi
  
  echo "  Config volume: $CONFIG_VOLUME"
  echo "  Models path: $MODELS_PATH"
  echo "  Port: $PORT"
  echo "  CUDA_VISIBLE_DEVICES: $CUDA_VISIBLE_DEVICES"
  
  # Stop and remove container
  echo "  Stopping container..."
  docker stop $CONTAINER
  
  echo "  Removing container..."
  docker rm $CONTAINER
  
  # Create new container with the same configuration
  echo "  Creating new container with latest image..."
  docker run -d \
    --name $CONTAINER \
    --restart always \
    -v $CONFIG_VOLUME:/root/.ollama \
    -v $MODELS_PATH:/root/.ollama/models \
    -p $PORT:11434 \
    -e OLLAMA_MODELS=/root/.ollama/models \
    -e OLLAMA_HOST=0.0.0.0:11434 \
    -e CUDA_VISIBLE_DEVICES=$CUDA_VISIBLE_DEVICES \
    --gpus all \
    ollama/ollama:latest
  
  # Check if container was created successfully
  if [ $? -ne 0 ]; then
    echo "  Error: Failed to create new container. Please check the error message above."
    continue
  fi
  
  echo "  Upgrade completed for $CONTAINER."
  echo
done

# Verify upgrade
echo "Verifying upgrade..."
verify_versions

echo
echo "Upgrade process completed."
echo "Please check that all containers are running correctly and models are accessible."
