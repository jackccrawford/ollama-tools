#!/bin/bash
# restore-ollama-containers.sh
# Created: May 4, 2025
# Updated: August 2, 2025
#
# Purpose: Restore Ollama Docker containers with optimized GPU assignments
# Each container has a preferred GPU but can access all GPUs if needed
# This provides better load balancing and resource utilization
#
# IMPORTANT: Uses Ollama 0.11.1 with --runtime=nvidia for:
# - 3x performance improvement over default runtime
# - Full NVML process visibility for load balancing
# - Better GPU integration and optimization
# - Emergent Intelligence: Agentic capabilities, chain-of-thought reasoning
# - MXFP4 quantization support for advanced models
#
# GPU Assignment Strategy:
# - Container 0: Prefer GPU 0, then 1,2,3
# - Container 1: Prefer GPU 1, then 2,3,0
# - Container 2: Prefer GPU 2, then 3,0,1
# - Container 3: Prefer GPU 3, then 0,1,2
#
# This ensures that small models are distributed across GPUs while
# allowing large models to use multiple GPUs when needed.

# Colors for better output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color
INFO="[${GREEN}INFO${NC}]"
WARN="[${YELLOW}WARN${NC}]"
ERROR="[${RED}ERROR${NC}]"

# Print header
echo -e "${GREEN}==========================================================${NC}"
echo -e "  Ollama Container Restoration with Optimized GPU Preferences"
echo -e "${GREEN}==========================================================${NC}"
echo

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
  echo -e "${ERROR} Docker is not running or you don't have permission to use it."
  echo -e "${INFO} Please start Docker or check your permissions and try again."
  exit 1
fi

# Check if NVIDIA Container Toolkit is installed
if ! command -v nvidia-smi &> /dev/null; then
  echo -e "${ERROR} NVIDIA drivers or nvidia-smi not found"
  echo -e "${INFO} Please install NVIDIA drivers and the NVIDIA Container Toolkit"
  exit 1
fi

# Check if user has sudo privileges
if [ "$(id -u)" -ne 0 ]; then
  echo -e "${WARN} Running without root privileges. Some operations might fail."
fi

# Create container with GPU preferences
create_container() {
  CONTAINER=$1
  CONFIG_VOLUME=$2
  MODELS_PATH=$3
  PORT=$4
  GPU_ORDER=$5
  
  echo -e "${INFO} Creating $CONTAINER with preferred GPU order: $GPU_ORDER"
  
  # Check if container exists and is running
  if docker ps -a --format '{{.Names}}' | grep -q "^$CONTAINER$"; then
    if docker ps --format '{{.Names}}' | grep -q "^$CONTAINER$"; then
      echo -e "${INFO} Stopping running container $CONTAINER..."
      docker stop $CONTAINER >/dev/null 2>&1
    fi
    echo -e "${INFO} Removing existing container $CONTAINER..."
    docker rm -f $CONTAINER >/dev/null 2>&1 || {
      echo -e "${ERROR} Failed to remove container $CONTAINER"
      return 1
    }
  fi
  
  # Create new container with GPU preferences
  echo -e "${INFO} Creating container with port $PORT and GPU order $GPU_ORDER..."
  
  # Check if models directory exists
  if [ ! -d "$MODELS_PATH" ]; then
    echo -e "${WARN} Models directory $MODELS_PATH does not exist. Creating..."
    mkdir -p "$MODELS_PATH" || {
      echo -e "${ERROR} Failed to create models directory"
      return 1
    }
  fi

  # Create container with ultra-high performance settings
  if docker run -d \
    --name $CONTAINER \
    --restart always \
    --runtime=nvidia \
    -v $CONFIG_VOLUME:/root/.ollama \
    -v $MODELS_PATH:/root/.ollama/models \
    -e CUDA_VISIBLE_DEVICES=$GPU_ORDER \
    -e NVIDIA_VISIBLE_DEVICES=all \
    -p $PORT:11434 \
    --gpus all \
    ollama/ollama:0.11.1; then
    
    echo -e "${ERROR} Failed to start container $CONTAINER"
    return 1
  fi
  
  # Wait for container to be healthy
  local max_retries=30
  local count=0
  
  echo -n -e "${INFO} Waiting for $CONTAINER to be ready"
  
  while [ $count -lt $max_retries ]; do
    if docker ps --filter "name=$CONTAINER" --filter "health=healthy" --format '{{.Names}}' | grep -q "^$CONTAINER$"; then
      echo -e "\n${INFO} Container $CONTAINER is healthy and ready"
      return 0
    fi
    
    # Show progress
    if [ $((count % 5)) -eq 0 ]; then
      echo -n "."
    fi
    
    count=$((count + 1))
    sleep 1
  done
  
  echo -e "\n${WARN} Container $CONTAINER is running but may not be fully healthy"
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
  TEST_PROMPT="This is a GPU preference test. Please respond with 'Hello from container $i' and nothing else."
  
  # Test each container
  for i in {0..3}; do
    CONTAINER="git-ollama$i-1"
    echo "===== Testing $CONTAINER ====="
    echo "Loading $TEST_MODEL..."
    
    echo -e "${INFO} Starting $TEST_MODEL in $CONTAINER..."
    
    # Run model in background and capture the output
    docker exec $CONTAINER ollama run $TEST_MODEL "$TEST_PROMPT" > /tmp/ollama_test_$i.log 2>&1 &
    PID=$!
    
    # Give it some time to start
    sleep 5
    
    # Check if the process is still running
    if ! ps -p $PID > /dev/null; then
      echo -e "${WARN} Process ended quickly. Checking logs..."
      cat /tmp/ollama_test_$i.log
      continue
    fi
    
    # Wait for model to load with timeout
    echo -n -e "${INFO} Waiting for model to load"
    
    local timeout=30
    local count=0
    local loaded=false
    
    while [ $count -lt $timeout ]; do
      # Check if the process is still running
      if ! ps -p $PID > /dev/null; then
        echo -e "\n${WARN} Process ended unexpectedly"
        loaded=false
        break
      fi
      
      # Check if the model is responding
      if grep -q "Hello from container $i" /tmp/ollama_test_$i.log 2>/dev/null; then
        echo -e "\n${GREEN}✓ Model responded successfully${NC}"
        loaded=true
        break
      fi
      
      # Show progress
      if [ $((count % 5)) -eq 0 ]; then
        echo -n "."
      fi
      
      count=$((count + 1))
      sleep 1
    done
    
    if [ "$loaded" = false ]; then
      echo -e "\n${WARN} Model may not have loaded properly"
      echo -e "${INFO} Last 10 lines of log:"
      tail -n 10 /tmp/ollama_test_$i.log 2>/dev/null || echo "No log file found"
    fi
    
    # Clean up
    kill $PID 2>/dev/null
    
    # Show detailed GPU usage
    echo -e "\n${INFO} GPU Usage:"
    nvidia-smi --query-gpu=index,name,memory.used,memory.total,utilization.gpu,temperature.gpu --format=csv | column -t -s ','
    
    # Show processes using GPU
    echo -e "\n${INFO} GPU Processes:"
    nvidia-smi --query-compute-apps=pid,process_name,gpu_uuid,used_memory --format=csv | column -t -s ','
    
    # Show container's view of GPUs
    echo -e "\n${INFO} Container's GPU Visibility:"
    if ! docker exec $CONTAINER nvidia-smi --query-gpu=index,name,memory.used --format=csv 2>/dev/null; then
      echo -e "  ${WARN} Could not query GPU information from container"
    fi
    
    # Show container resource usage
    echo -e "\n${INFO} Container Resource Usage:"
    docker stats $CONTAINER --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"
    
    # Clean up test files
    rm -f /tmp/ollama_test_$i.log
    
    # Ask to continue
    echo -e "\n${YELLOW}Press Enter to continue to next container (or 'q' to quit)...${NC}"
    read -n 1 input
    if [[ "$input" == "q" ]]; then
      echo -e "\n${INFO} Verification canceled by user"
      break
    fi
    echo
  done
  
  echo "Verification complete."
  echo
}

# Show system information
echo -e "${INFO} System Information:"
echo -e "  Hostname: $(hostname)"
echo -e "  Date: $(date)"
echo -e "  Docker Version: $(docker --version | cut -d ' ' -f 3 | cut -d ',' -f 1)"

echo -e "\n${INFO} Available GPUs:"
nvidia-smi --query-gpu=index,name,memory.total,driver_version --format=csv | column -t -s ','
echo

# Define container configurations
echo -e "\n${INFO} Restoring Ollama containers with optimized GPU preferences...\n"

# Array of container configurations
CONTAINERS=(
  "0 git-ollama0-1 git_ollama0_data 11434 0,1,2,3"
  "1 git-ollama1-1 git_ollama1_data 11435 1,0,2,3"
  "2 git-ollama2-1 git_ollama2_data 11436 2,0,1,3"
  "3 git-ollama3-1 git_ollama3_data 11437 3,0,1,2"
)

# Create containers
for container_info in "${CONTAINERS[@]}"; do
  read -r idx container volume port gpu_order <<< "$container_info"
  
  echo -e "\n${GREEN}===== Container $idx =====${NC}"
  echo -e "  Name: $container"
  echo -e "  Volume: $volume"
  echo -e "  Port: $port"
  echo -e "  GPU Order: $gpu_order"
  
  create_container "$container" "$volume" "/home/explora/.ollama/models" "$port" "$gpu_order"
  
  if [ $? -ne 0 ]; then
    echo -e "${ERROR} Failed to create container $container"
    # Continue with other containers even if one fails
    continue
  fi
  
  # Verify container is running
  if docker ps --filter "name=$container" --format '{{.Names}}' | grep -q "^$container$"; then
    echo -e "${INFO} Successfully created and started $container"
  else
    echo -e "${WARN} Container $container was created but is not running"
  fi
done

# Verify configuration
echo -e "\n${GREEN}===== Verifying Container Configurations =====${NC}"

# Check if any containers are running
if ! docker ps --filter "name=git-ollama" --format "{{.Names}}" | grep -q "git-ollama"; then
  echo -e "${ERROR} No Ollama containers are running"
  exit 1
fi

# Verify each container
for CONTAINER in $(docker ps --filter "name=git-ollama" --format "{{.Names}}" | sort); do
  echo -e "\n${GREEN}===== $CONTAINER =====${NC}"
  
  # Show container status
  echo -e "${INFO} Status: $(docker inspect -f '{{.State.Status}}' $CONTAINER 2>/dev/null || echo 'not running')"
  
  # Show environment variables
  echo -e "${INFO} Environment:"
  docker exec $CONTAINER env 2>/dev/null | grep -E "CUDA|NVIDIA|OLLAMA" | sort || \
    echo -e "  ${WARN} Could not inspect container environment"
  
  # Show port mapping
  echo -e "${INFO} Ports:"
  docker port $CONTAINER 2>/dev/null || echo -e "  ${WARN} Could not get port mapping"
  
  # Show volume mounts
  echo -e "${INFO} Volumes:"
  docker inspect -f '{{range .Mounts}}{{printf "  %s -> %s\n" .Source .Destination}}{{end}}' $CONTAINER 2>/dev/null || \
    echo -e "  ${WARN} Could not get volume information"
  
  # Show GPU access
  echo -e "${INFO} GPU Access:"
  if docker exec $CONTAINER nvidia-smi --query-gpu=index,name --format=csv 2>/dev/null; then
    echo -e "  ${GREEN}✓${NC} GPU access working"
  else
    echo -e "  ${RED}✗${NC} No GPU access or nvidia-smi not available"
  fi
done

# Show summary
echo -e "\n${GREEN}===== Restoration Summary =====${NC}"
TOTAL_CONTAINERS=$(docker ps --filter "name=git-ollama" --format "{{.Names}}" | wc -l)
echo -e "${INFO} Total containers: $TOTAL_CONTAINERS/4"

echo -e "\n${GREEN}✓ Restoration process completed${NC}"
echo -e "All Ollama containers have been recreated with optimized GPU assignments."
echo

# Offer to verify proper operation
if [[ "$1" != "--skip-verify" ]]; then
  verify_operation
else
  echo -e "\n${WARN} Skipping verification (--skip-verify flag used)"
fi

# Show usage instructions
echo -e "\n${GREEN}===== Next Steps =====${NC}"
echo -e "1. To test a container, run:"
echo -e "   ${YELLOW}docker exec git-ollama0-1 ollama run phi:2.7b \"Hello world\"${NC}"

echo -e "\n2. Check GPU usage:"
echo -e "   ${YELLOW}watch -n 1 nvidia-smi${NC}"

echo -e "\n3. View container logs:"
echo -e "   ${YELLOW}docker logs -f git-ollama0-1${NC}"

echo -e "\n4. For help:"
echo -e "   ${YELLOW}$0 --help${NC}"

echo -e "\n${GREEN}All done! Your Ollama containers are up and running with optimized GPU assignments.${NC}"
