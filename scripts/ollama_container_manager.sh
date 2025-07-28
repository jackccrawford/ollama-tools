#!/bin/bash
# ollama_container_manager.sh
# A utility script to manage Ollama GPU-enabled containers
# Created on: 2025-06-18

set -e

# Configuration
MODEL_DIR="/home/explora/.ollama/models"
BASE_PORT=11434
CONTAINER_PREFIX="git-ollama"
IMAGE="ollama/ollama:0.9.2"

# Function to show usage
show_usage() {
  echo "Ollama Container Manager"
  echo "Usage: $0 [command]"
  echo ""
  echo "Commands:"
  echo "  status             - Show status of all Ollama containers"
  echo "  start [id]         - Start container with ID (0-3), or all if no ID specified"
  echo "  stop [id]          - Stop container with ID (0-3), or all if no ID specified"
  echo "  restart [id]       - Restart container with ID (0-3), or all if no ID specified"
  echo "  recreate [id]      - Recreate container with ID (0-3) with GPU support, or all if no ID specified"
  echo "  logs [id]          - Show logs for container with ID (0-3)"
  echo "  gpu-status         - Show GPU utilization status"
  echo "  models             - List available models across all containers"
  echo ""
  echo "Examples:"
  echo "  $0 status          - Show status of all containers"
  echo "  $0 start 2         - Start container with ID 2 (port 11436)"
  echo "  $0 recreate        - Recreate all containers with GPU support"
}

# Function to check if container exists
container_exists() {
  local id=$1
  docker ps -a --format "{{.Names}}" | grep -q "${CONTAINER_PREFIX}${id}-1"
  return $?
}

# Function to get container status
get_status() {
  echo "===== Ollama Container Status ====="
  docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep ${CONTAINER_PREFIX} || echo "No Ollama containers found"
  echo ""
  
  # Check if containers have GPU access
  echo "===== GPU Detection Status ====="
  for i in {0..3}; do
    if container_exists $i; then
      echo -n "${CONTAINER_PREFIX}${i}-1: "
      if docker logs ${CONTAINER_PREFIX}${i}-1 2>&1 | grep -q "inference compute.*library=cuda"; then
        echo "GPU detected ✓"
      else
        echo "No GPU detected ✗"
      fi
    fi
  done
}

# Function to start container
start_container() {
  local id=$1
  if container_exists $id; then
    echo "Starting ${CONTAINER_PREFIX}${id}-1..."
    docker start ${CONTAINER_PREFIX}${id}-1
  else
    echo "Container ${CONTAINER_PREFIX}${id}-1 does not exist. Use 'recreate' command to create it."
  fi
}

# Function to stop container
stop_container() {
  local id=$1
  if container_exists $id; then
    echo "Stopping ${CONTAINER_PREFIX}${id}-1..."
    docker stop ${CONTAINER_PREFIX}${id}-1
  else
    echo "Container ${CONTAINER_PREFIX}${id}-1 does not exist."
  fi
}

# Function to recreate container with GPU support
recreate_container() {
  local id=$1
  local port=$((BASE_PORT + id))
  
  # Stop and remove if exists
  if container_exists $id; then
    echo "Stopping and removing existing ${CONTAINER_PREFIX}${id}-1..."
    docker stop ${CONTAINER_PREFIX}${id}-1 2>/dev/null || true
    docker rm ${CONTAINER_PREFIX}${id}-1 2>/dev/null || true
  fi
  
  # Create new container with GPU support
  echo "Creating ${CONTAINER_PREFIX}${id}-1 with GPU support on port ${port}..."
  docker run -d --gpus all --name ${CONTAINER_PREFIX}${id}-1 \
    --restart always \
    -p ${port}:11434 \
    -v ${MODEL_DIR}:/root/.ollama/models \
    ${IMAGE}
    
  echo "Waiting for container to initialize..."
  sleep 5
  
  # Verify GPU detection
  if docker logs ${CONTAINER_PREFIX}${id}-1 2>&1 | grep -q "inference compute.*library=cuda"; then
    echo "✓ GPU successfully detected in ${CONTAINER_PREFIX}${id}-1"
  else
    echo "✗ WARNING: GPU not detected in ${CONTAINER_PREFIX}${id}-1"
  fi
}

# Function to show container logs
show_logs() {
  local id=$1
  if container_exists $id; then
    docker logs ${CONTAINER_PREFIX}${id}-1 | grep -i "gpu\|cuda\|inference compute"
  else
    echo "Container ${CONTAINER_PREFIX}${id}-1 does not exist."
  fi
}

# Function to show GPU status
show_gpu_status() {
  echo "===== GPU Status ====="
  nvidia-smi
}

# Function to list models
list_models() {
  echo "===== Available Models ====="
  for i in {0..3}; do
    if container_exists $i && docker ps --format "{{.Names}}" | grep -q "${CONTAINER_PREFIX}${i}-1"; then
      local port=$((BASE_PORT + i))
      echo "Models on ${CONTAINER_PREFIX}${i}-1 (port ${port}):"
      curl -s http://localhost:${port}/api/tags | jq -r '.models[] | "  - " + .name + " (" + (.details.parameter_size // "unknown") + ")"' 2>/dev/null || echo "  Error retrieving models"
      echo ""
    fi
  done
}

# Main command processing
case "$1" in
  status)
    get_status
    ;;
  start)
    if [ -z "$2" ]; then
      for i in {0..3}; do
        start_container $i
      done
    else
      start_container $2
    fi
    ;;
  stop)
    if [ -z "$2" ]; then
      for i in {0..3}; do
        stop_container $i
      done
    else
      stop_container $2
    fi
    ;;
  restart)
    if [ -z "$2" ]; then
      for i in {0..3}; do
        stop_container $i
        start_container $i
      done
    else
      stop_container $2
      start_container $2
    fi
    ;;
  recreate)
    if [ -z "$2" ]; then
      for i in {0..3}; do
        recreate_container $i
      done
    else
      recreate_container $2
    fi
    ;;
  logs)
    if [ -z "$2" ]; then
      echo "Please specify a container ID (0-3)"
      exit 1
    else
      show_logs $2
    fi
    ;;
  gpu-status)
    show_gpu_status
    ;;
  models)
    list_models
    ;;
  *)
    show_usage
    exit 1
    ;;
esac

exit 0
