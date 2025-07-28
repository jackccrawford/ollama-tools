#!/bin/bash
# assign-ollama-gpu-preferences.sh
# Created: May 4, 2025
#
# Purpose: Configure Ollama Docker containers with preferred GPU assignments
# Each container will prefer a specific initial GPU while still having access to all GPUs if needed
# This helps prevent blocking for small model footprints (under 12GB) by distributing them across GPUs

# Print header
echo "=========================================================="
echo "  Ollama Container GPU Preference Configuration"
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
  echo "  -c, --check-only       Check current configuration without updating"
  echo "  -f, --force            Force update without confirmation"
  echo
  echo "Example:"
  echo "  $0                     Interactive update with confirmation"
  echo "  $0 --force             Update all containers without confirmation"
  echo "  $0 --check-only        Only check current configuration"
}

# Parse command line arguments
CHECK_ONLY=false
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
  echo "Checking current Ollama container GPU configuration..."
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
  
  echo "Current GPU configuration:"
  for CONTAINER in $CONTAINERS; do
    echo "===== $CONTAINER ====="
    echo "NVIDIA environment variables:"
    docker exec $CONTAINER env | grep -E "NVIDIA|CUDA" 2>/dev/null || echo "  No GPU environment variables found"
    
    echo "GPU device requests:"
    docker inspect $CONTAINER --format '{{json .HostConfig.DeviceRequests}}' 2>/dev/null | jq . || echo "  Unable to get GPU device requests"
    echo
  done
  
  # Show available GPUs
  echo "Available GPUs on the system:"
  nvidia-smi --query-gpu=index,name,memory.total --format=csv,noheader
  echo
}

# Function to update container with GPU preferences
update_container() {
  CONTAINER=$1
  PORT=$2
  PREFERRED_GPU=$3
  GPU_ORDER=$4
  
  echo "Updating $CONTAINER (Port $PORT) with preferred GPU order: $GPU_ORDER..."
  
  # Get container configuration
  CONFIG_VOLUME=$(docker inspect $CONTAINER --format '{{range .Mounts}}{{if eq .Destination "/root/.ollama"}}{{if eq .Type "volume"}}{{.Name}}{{end}}{{end}}{{end}}' 2>/dev/null)
  MODELS_PATH=$(docker inspect $CONTAINER --format '{{range .Mounts}}{{if eq .Destination "/root/.ollama/models"}}{{if eq .Type "bind"}}{{.Source}}{{end}}{{end}}{{end}}' 2>/dev/null)
  
  # Check if we got all required configuration
  if [ -z "$CONFIG_VOLUME" ] || [ -z "$MODELS_PATH" ]; then
    echo "  Error: Could not get complete configuration for $CONTAINER. Skipping."
    return 1
  fi
  
  echo "  Config volume: $CONFIG_VOLUME"
  echo "  Models path: $MODELS_PATH"
  echo "  Port: $PORT"
  echo "  Preferred GPU order: $GPU_ORDER"
  
  # Stop and remove container
  echo "  Stopping container..."
  docker stop $CONTAINER
  
  echo "  Removing container..."
  docker rm $CONTAINER
  
  # Create new container with GPU preferences
  echo "  Creating new container with GPU preferences..."
  docker run -d \
    --name $CONTAINER \
    --restart always \
    -v $CONFIG_VOLUME:/root/.ollama \
    -v $MODELS_PATH:/root/.ollama/models \
    -p $PORT:11434 \
    -e OLLAMA_MODELS=/root/.ollama/models \
    -e OLLAMA_HOST=0.0.0.0:11434 \
    -e NVIDIA_VISIBLE_DEVICES=all \
    -e CUDA_VISIBLE_DEVICES=$GPU_ORDER \
    --gpus all \
    ollama/ollama:latest
  
  # Check if container was created successfully
  if [ $? -ne 0 ]; then
    echo "  Error: Failed to create new container. Please check the error message above."
    return 1
  fi
  
  echo "  Update completed for $CONTAINER."
  echo
  return 0
}

# Check current configuration
check_configuration

# Exit if only checking configuration
if [ "$CHECK_ONLY" = true ]; then
  exit 0
fi

# Confirm update
if [ "$FORCE" = false ]; then
  echo -n "Do you want to update these Ollama containers with preferred GPU assignments? (y/N): "
  read CONFIRM
  if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
    echo "Update cancelled."
    exit 0
  fi
fi

# Define container configurations
# Format: container_name, port, preferred_gpu, gpu_order
CONTAINER_CONFIGS=(
  "git-ollama0-1 11434 0 0,1,2,3"
  "git-ollama1-1 11435 1 1,0,2,3"
  "git-ollama2-1 11436 2 2,0,1,3"
  "git-ollama3-1 11437 3 3,0,1,2"
)

# Update each container
SUCCESS_COUNT=0
TOTAL_COUNT=${#CONTAINER_CONFIGS[@]}

for CONFIG in "${CONTAINER_CONFIGS[@]}"; do
  read -r CONTAINER PORT PREFERRED_GPU GPU_ORDER <<< "$CONFIG"
  
  # Check if container exists
  if ! docker ps -a --filter "name=$CONTAINER" --format "{{.Names}}" | grep -q "$CONTAINER"; then
    echo "Container $CONTAINER not found. Skipping."
    continue
  fi
  
  # Update container
  update_container "$CONTAINER" "$PORT" "$PREFERRED_GPU" "$GPU_ORDER"
  if [ $? -eq 0 ]; then
    ((SUCCESS_COUNT++))
  fi
done

# Verify configuration
echo "Verifying GPU preferences..."
for CONTAINER in $(docker ps --filter "name=git-ollama" --format "{{.Names}}"); do
  PORT=$(docker inspect $CONTAINER --format '{{range $p, $conf := .NetworkSettings.Ports}}{{if eq $p "11434/tcp"}}{{(index $conf 0).HostPort}}{{end}}{{end}}')
  echo "===== $CONTAINER (Port $PORT) ====="
  echo "GPU preferences:"
  docker exec $CONTAINER env | grep -E "CUDA|NVIDIA"
  echo
done

echo
echo "Update process completed: $SUCCESS_COUNT of $TOTAL_COUNT containers updated successfully."
echo "Please check that all containers are running correctly with their preferred GPU assignments."
echo
echo "To test the configuration, load a small model in each container and verify that it uses the preferred GPU."
echo "For example: docker exec git-ollama0-1 ollama run phi:2.7b \"Hello world\""
echo "Then check GPU usage with: nvidia-smi"
