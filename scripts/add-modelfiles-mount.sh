#!/bin/bash
# add-modelfiles-mount.sh
# Created: July 28, 2025
#
# Purpose: Add Modelfiles mount to existing Ollama containers to enable custom model creation
# This script temporarily adds a mount for Modelfiles, preserving all existing configurations

# Print header
echo "=========================================================="
echo "  Ollama Modelfiles Mount Addition Script"
echo "=========================================================="
echo

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
  echo "Error: Docker is not running or you don't have permission to use it."
  echo "Please start Docker or check your permissions and try again."
  exit 1
fi

# Configuration
CONTAINER_PREFIX="git-ollama"
BASE_PORT=11434

# Function to display usage
usage() {
  echo "Usage: $0 [OPTIONS] MODELFILES_PATH"
  echo
  echo "Add Modelfiles mount to Ollama containers for custom model creation"
  echo
  echo "Arguments:"
  echo "  MODELFILES_PATH        Path to directory containing Modelfiles (required)"
  echo
  echo "Options:"
  echo "  -h, --help             Display this help message"
  echo "  -c, --container ID     Only modify specific container (0-3)"
  echo "  -d, --dry-run          Show what would be done without making changes"
  echo "  -f, --force            Skip confirmation prompts"
  echo
  echo "Examples:"
  echo "  $0 /home/explora/dev/tin-sidekick-sdr/ollama-agents"
  echo "  $0 -c 0 /path/to/modelfiles"
  echo "  $0 --dry-run /path/to/modelfiles"
}

# Parse command line arguments
CONTAINER_ID=""
DRY_RUN=false
FORCE=false
MODELFILES_PATH=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help)
      usage
      exit 0
      ;;
    -c|--container)
      CONTAINER_ID="$2"
      if [[ ! "$CONTAINER_ID" =~ ^[0-3]$ ]]; then
        echo "Error: Container ID must be 0, 1, 2, or 3"
        exit 1
      fi
      shift 2
      ;;
    -d|--dry-run)
      DRY_RUN=true
      shift
      ;;
    -f|--force)
      FORCE=true
      shift
      ;;
    -*)
      echo "Error: Unknown option $1"
      usage
      exit 1
      ;;
    *)
      if [[ -z "$MODELFILES_PATH" ]]; then
        MODELFILES_PATH="$1"
      else
        echo "Error: Multiple paths specified. Only one path is allowed."
        usage
        exit 1
      fi
      shift
      ;;
  esac
done

# Validate required arguments
if [[ -z "$MODELFILES_PATH" ]]; then
  echo "Error: Modelfiles path is required"
  usage
  exit 1
fi

# Validate modelfiles path exists
if [[ ! -d "$MODELFILES_PATH" ]]; then
  echo "Error: Modelfiles path does not exist: $MODELFILES_PATH"
  exit 1
fi

# Convert to absolute path
MODELFILES_PATH=$(realpath "$MODELFILES_PATH")

echo "Modelfiles path: $MODELFILES_PATH"
echo

# Function to get container configuration
get_container_config() {
  local container=$1
  
  # Get models path (bind mount)
  local models_path=$(docker inspect $container --format '{{range .Mounts}}{{if eq .Destination "/root/.ollama/models"}}{{.Source}}{{end}}{{end}}' 2>/dev/null)
  
  # Get port mapping
  local port=$(docker inspect $container --format '{{range $p, $conf := .NetworkSettings.Ports}}{{if eq $p "11434/tcp"}}{{(index $conf 0).HostPort}}{{end}}{{end}}' 2>/dev/null)
  
  # Get GPU order from environment
  local gpu_order=$(docker inspect $container --format '{{range .Config.Env}}{{if (index (split . "=") 0 | eq "CUDA_VISIBLE_DEVICES")}}{{index (split . "=") 1}}{{end}}{{end}}' 2>/dev/null)
  
  # For bind mount setup, we don't have a separate config volume - models path serves as the base
  local config_volume="git_ollama$(echo $container | grep -o '[0-9]' | tr -d '\n')_data"
  
  echo "$config_volume|$models_path|$port|$gpu_order"
}

# Function to recreate container with modelfiles mount
recreate_container_with_modelfiles() {
  local id=$1
  local container="${CONTAINER_PREFIX}${id}-1"
  
  echo "Processing container: $container"
  
  # Check if container exists
  if ! docker ps -a --format '{{.Names}}' | grep -q "^$container$"; then
    echo "  Container $container does not exist. Skipping."
    return 0
  fi
  
  # Get current configuration
  local config=$(get_container_config $container)
  IFS='|' read -r config_volume models_path port gpu_order <<< "$config"
  
  if [[ -z "$models_path" || -z "$port" ]]; then
    echo "  Error: Could not retrieve configuration for $container"
    return 1
  fi
  
  # GPU order might be empty for containers without explicit CUDA settings
  if [[ -z "$gpu_order" ]]; then
    gpu_order="all"
  fi
  
  echo "  Current configuration:"
  echo "    Config volume: $config_volume"
  echo "    Models path: $models_path"
  echo "    Port: $port"
  echo "    GPU order: $gpu_order"
  
  if [[ "$DRY_RUN" == "true" ]]; then
    echo "  [DRY RUN] Would recreate container with modelfiles mount: $MODELFILES_PATH:/modelfiles"
    return 0
  fi
  
  # Stop and remove existing container
  echo "  Stopping and removing existing container..."
  docker stop $container >/dev/null 2>&1 || true
  docker rm $container >/dev/null 2>&1 || true
  
  # Create new container with modelfiles mount
  echo "  Creating container with modelfiles mount..."
  docker run -d \
    --name $container \
    --restart always \
    -v $models_path:/root/.ollama/models \
    -v $MODELFILES_PATH:/modelfiles \
    -p $port:11434 \
    --gpus all \
    ollama/ollama:latest
  
  # Check if container was created successfully
  if [ $? -ne 0 ]; then
    echo "  Error: Failed to create new container. Please check the error message above."
    return 1
  fi
  
  echo "  Container recreated successfully with modelfiles mount."
  
  # Wait for container to initialize
  echo "  Waiting for container to initialize..."
  sleep 5
  
  # Verify the container is running and modelfiles are accessible
  if docker exec $container ls /modelfiles >/dev/null 2>&1; then
    echo "  ✓ Modelfiles mount verified: /modelfiles is accessible"
  else
    echo "  ✗ Warning: Modelfiles mount may not be working properly"
  fi
  
  echo
  return 0
}

# Show current container status
echo "Current container status:"
docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep ${CONTAINER_PREFIX} || echo "No Ollama containers found"
echo

# Determine which containers to process
if [[ -n "$CONTAINER_ID" ]]; then
  CONTAINERS=($CONTAINER_ID)
else
  CONTAINERS=(0 1 2 3)
fi

# Confirmation prompt
if [[ "$FORCE" != "true" && "$DRY_RUN" != "true" ]]; then
  echo "This will recreate the following containers with modelfiles mount:"
  for id in "${CONTAINERS[@]}"; do
    container="${CONTAINER_PREFIX}${id}-1"
    if docker ps -a --format '{{.Names}}' | grep -q "^$container$"; then
      echo "  - $container"
    fi
  done
  echo
  echo "Modelfiles will be mounted at: $MODELFILES_PATH:/modelfiles"
  echo
  read -p "Do you want to continue? (y/N): " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Operation cancelled."
    exit 0
  fi
  echo
fi

# Process containers
SUCCESS_COUNT=0
TOTAL_COUNT=0

for id in "${CONTAINERS[@]}"; do
  container="${CONTAINER_PREFIX}${id}-1"
  if docker ps -a --format '{{.Names}}' | grep -q "^$container$"; then
    TOTAL_COUNT=$((TOTAL_COUNT + 1))
    if recreate_container_with_modelfiles $id; then
      SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    fi
  fi
done

# Summary
echo "=========================================================="
if [[ "$DRY_RUN" == "true" ]]; then
  echo "Dry run completed. $TOTAL_COUNT containers would be processed."
else
  echo "Operation completed: $SUCCESS_COUNT/$TOTAL_COUNT containers successfully updated."
  
  if [[ $SUCCESS_COUNT -gt 0 ]]; then
    echo
    echo "Modelfiles are now accessible at /modelfiles inside the containers."
    echo "You can create custom models using:"
    echo "  ollama create model-name -f /modelfiles/path/to/Modelfile"
  fi
fi
echo "=========================================================="
