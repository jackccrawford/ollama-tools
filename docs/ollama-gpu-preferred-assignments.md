# Ollama Container GPU Preferred Assignments

## Optimized GPU Configuration

Your system has 4 NVIDIA TITAN Xp GPUs, each with 12GB of memory. We can configure each Ollama container to prefer a specific initial GPU while still allowing access to others when needed.

### Available GPUs

```
+-----------------------------------------------------------------------------------------+
| GPU  Name                                | Bus-Id          | Memory                      |
|=========================================+========================+======================|
|   0  NVIDIA TITAN Xp COLLECTORS EDITION  | 00000000:02:00.0      | 12GB                   |
|   1  NVIDIA TITAN Xp                     | 00000000:03:00.0      | 12GB                   |
|   2  NVIDIA TITAN Xp COLLECTORS EDITION  | 00000000:04:00.0      | 12GB                   |
|   3  NVIDIA TITAN Xp                     | 00000000:05:00.0      | 12GB                   |
+-----------------------------------------------------------------------------------------+
```

## Optimized Configuration Approach

We'll use a combination of environment variables to achieve the preferred GPU assignment:

1. Keep `NVIDIA_VISIBLE_DEVICES=all` so each container can access all GPUs if needed
2. Add `CUDA_VISIBLE_DEVICES` to set the preferred order of GPUs for each container

This approach ensures:
- Each container initially tries to use its preferred GPU first
- If more memory is needed, it can expand to other GPUs in the specified order
- Small models (under 12GB) will naturally distribute across different GPUs
- Large models can still span multiple GPUs as needed

## Implementation Plan

Here's how to update each container with a preferred GPU while maintaining access to all GPUs:

```bash
# For git-ollama0-1 (prefer GPU 0, then others)
docker stop git-ollama0-1
docker rm git-ollama0-1
docker run -d --name git-ollama0-1 --restart always \
  --runtime=nvidia \
  --shm-size=2g \
  --ulimit memlock=-1 \
  --ulimit stack=67108864 \
  -v /home/explora/.ollama/models:/root/.ollama/models \
  -v git_ollama0_data:/root/.ollama \
  -p 11434:11434 \
  -e OLLAMA_MODELS=/root/.ollama/models \
  -e OLLAMA_HOST=0.0.0.0:11434 \
  -e NVIDIA_VISIBLE_DEVICES=all \
  -e CUDA_VISIBLE_DEVICES=0,1,2,3 \
  --gpus all \
  ollama/ollama:latest

# For git-ollama1-1 (prefer GPU 1, then others)
docker stop git-ollama1-1
docker rm git-ollama1-1
docker run -d --name git-ollama1-1 --restart always \
  -v git_ollama1_data:/root/.ollama \
  -v /home/explora/.ollama/models:/root/.ollama/models \
  -p 11435:11434 \
  -e OLLAMA_MODELS=/root/.ollama/models \
  -e OLLAMA_HOST=0.0.0.0:11434 \
  -e NVIDIA_VISIBLE_DEVICES=all \
  -e CUDA_VISIBLE_DEVICES=1,0,2,3 \
  --gpus all \
  ollama/ollama:latest

# For git-ollama2-1 (prefer GPU 2, then others)
docker stop git-ollama2-1
docker rm git-ollama2-1
docker run -d --name git-ollama2-1 --restart always \
  -v git_ollama2_data:/root/.ollama \
  -v /home/explora/.ollama/models:/root/.ollama/models \
  -p 11436:11434 \
  -e OLLAMA_MODELS=/root/.ollama/models \
  -e OLLAMA_HOST=0.0.0.0:11434 \
  -e NVIDIA_VISIBLE_DEVICES=all \
  -e CUDA_VISIBLE_DEVICES=2,0,1,3 \
  --gpus all \
  ollama/ollama:latest

# For git-ollama3-1 (prefer GPU 3, then others)
docker stop git-ollama3-1
docker rm git-ollama3-1
docker run -d --name git-ollama3-1 --restart always \
  -v /home/explora/.ollama/models:/root/.ollama/models \
  -v git_ollama3_data:/root/.ollama \
  -p 11437:11434 \
  -e OLLAMA_MODELS=/root/.ollama/models \
  -e OLLAMA_HOST=0.0.0.0:11434 \
  -e NVIDIA_VISIBLE_DEVICES=all \
  -e CUDA_VISIBLE_DEVICES=3,0,1,2 \
  --gpus all \
  ollama/ollama:latest
```

## Benefits of This Approach

This configuration provides several advantages:

1. **3x Performance Improvement**: NVIDIA runtime provides significantly faster inference
2. **Initial Load Balancing**: Each container will first try to use its preferred GPU
3. **Full Process Visibility**: Essential for orchestration and load balancing systems
4. **No Blocking for Small Models**: Models under 12GB will naturally distribute across GPUs
5. **Flexibility for Large Models**: Larger models can still span multiple GPUs efficiently
6. **Real-time Monitoring**: `nvidia-smi` shows all containerized processes and GPU usage
7. **Graceful Degradation**: If GPUs are full, processing can fall back to CPU
8. **Efficient Resource Utilization**: All GPU memory can be utilized optimally

## Verifying the Configuration

After updating the containers, you can verify the configuration with:

```bash
for i in {0..3}; do 
  echo "===== CONTAINER git-ollama$i-1 ====="; 
  docker exec git-ollama$i-1 env | grep CUDA; 
  echo; 
done
```

## Testing the Configuration

To test if the configuration is working as expected:

1. Load a small model (under 12GB) in each container
2. Run `nvidia-smi` to see which GPU each model is loaded into
3. Verify that each container is using its preferred GPU

For larger models that exceed 12GB, you should see them span multiple GPUs in the order specified by `CUDA_VISIBLE_DEVICES`.

## Updating the Upgrade Script

If you implement this configuration, you should update the upgrade script (`~/bin/upgrade-ollama-containers.sh`) to preserve these GPU preferences during future upgrades.
