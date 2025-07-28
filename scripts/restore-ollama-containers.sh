#!/bin/bash
# restore-ollama-containers.sh
# Created: May 4, 2025
#
# Purpose: Restore Ollama Docker containers with preferred GPU assignments
# Each container will prefer a specific initial GPU while still having access to all GPUs if needed

# Print header
echo "=========================================================="
echo "  Ollama Container Restoration with GPU Preferences"
echo "=========================================================="
echo

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
  echo "Error: Docker is not running or you don't have permission to use it."
  echo "Please start Docker or check your permissions and try again."
  exit 1
fi

# Create container with GPU preferences
create_container() {
  CONTAINER=$1
  CONFIG_VOLUME=$2
  MODELS_PATH=$3
  PORT=$4
  GPU_ORDER=$5
  
  echo "Creating $CONTAINER with preferred GPU order: $GPU_ORDER..."
  
  # Remove container if it exists
  if docker ps -a --format '{{.Names}}' | grep -q "^$CONTAINER$"; then
    echo "  Container $CONTAINER exists. Removing it..."
    docker rm -f $CONTAINER >/dev/null 2>&1
  fi
  
  # Create new container with GPU preferences
  echo "  Creating container..."
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
    echo "  Error: Failed to create container. Please check the error message above."
    return 1
  fi
  
  echo "  Container created successfully."
  echo
  return 0
}

# Function to verify proper operation by testing each container
verify_operation() {
  echo "Would you like to verify proper operation by testing each container? (y/N): "
  read VERIFY
  if [[ ! "$VERIFY" =~ ^[Yy]$ ]]; then
    return 0
  fi
  
  echo
  echo "Running verification tests..."
  echo "This will load a small model in each container and check GPU usage."
  echo

  # Small test model
  TEST_MODEL="phi:2.7b"
  TEST_PROMPT="This is a GPU preference test"
  
  # Test each container
  for i in {0..3}; do
    CONTAINER="git-ollama$i-1"
    echo "===== Testing $CONTAINER ====="
    echo "Loading $TEST_MODEL..."
    
    # Run model in background
    docker exec -d $CONTAINER ollama run $TEST_MODEL "$TEST_PROMPT" > /dev/null 2>&1
    
    # Wait for model to load
    echo "Waiting for model to load (5 seconds)..."
    sleep 5
    
    # Check GPU usage
    echo "GPU usage:"
    nvidia-smi --query-gpu=index,name,memory.used,utilization.gpu --format=csv,noheader
    
    # Show which GPU is being used by this container
    echo "Process information:"
    nvidia-smi --query-compute-apps=gpu_uuid,pid,used_memory --format=csv,noheader | \
      grep -i ollama
    
    echo
    echo "Press Enter to continue to next container..."
    read
  done
  
  echo "Verification complete."
  echo
}

# Show available GPUs
echo "Available GPUs on the system:"
nvidia-smi --query-gpu=index,name,memory.total --format=csv,noheader
echo

# Define container configurations
echo "Restoring Ollama containers with GPU preferences..."
echo

# Container 0: Prefer GPU 0
create_container "git-ollama0-1" "git_ollama0_data" "/home/explora/.ollama/models" "11434" "0,1,2,3"

# Container 1: Prefer GPU 1
create_container "git-ollama1-1" "git_ollama1_data" "/home/explora/.ollama/models" "11435" "1,0,2,3"

# Container 2: Prefer GPU 2
create_container "git-ollama2-1" "git_ollama2_data" "/home/explora/.ollama/models" "11436" "2,0,1,3"

# Container 3: Prefer GPU 3
create_container "git-ollama3-1" "git_ollama3_data" "/home/explora/.ollama/models" "11437" "3,0,1,2"

# Verify configuration
echo "Verifying GPU preferences..."
for CONTAINER in $(docker ps --filter "name=git-ollama" --format "{{.Names}}"); do
  echo "===== $CONTAINER ====="
  echo "GPU preferences:"
  docker exec $CONTAINER env | grep -E "CUDA|NVIDIA"
  echo
done

echo
echo "Restoration process completed."
echo "All Ollama containers have been recreated with preferred GPU assignments."
echo

# Offer to verify proper operation
verify_operation

echo "To manually test the configuration, load a small model in each container and verify that it uses the preferred GPU."
echo "For example: docker exec git-ollama0-1 ollama run phi:2.7b \"Hello world\""
echo "Then check GPU usage with: nvidia-smi"
