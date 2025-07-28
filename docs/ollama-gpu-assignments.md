# Ollama Container GPU Assignments

## Current Configuration

Your system has 4 NVIDIA TITAN Xp GPUs, and your Ollama containers are currently configured to access all GPUs rather than being restricted to specific ones.

### Available GPUs

```
+-----------------------------------------------------------------------------------------+
| GPU  Name                                | Bus-Id          | Index                       |
|=========================================+========================+======================|
|   0  NVIDIA TITAN Xp COLLECTORS EDITION  | 00000000:02:00.0      | GPU 0                  |
|   1  NVIDIA TITAN Xp                     | 00000000:03:00.0      | GPU 1                  |
|   2  NVIDIA TITAN Xp COLLECTORS EDITION  | 00000000:04:00.0      | GPU 2                  |
|   3  NVIDIA TITAN Xp                     | 00000000:05:00.0      | GPU 3                  |
+-----------------------------------------------------------------------------------------+
```

### Current Container Settings

| Container      | GPU Setting              | Effect                                   |
|----------------|--------------------------|------------------------------------------|
| git-ollama0-1  | NVIDIA_VISIBLE_DEVICES=all | Can access all GPUs (0, 1, 2, 3)         |
| git-ollama1-1  | NVIDIA_VISIBLE_DEVICES=all | Can access all GPUs (0, 1, 2, 3)         |
| git-ollama2-1  | NVIDIA_VISIBLE_DEVICES=all | Can access all GPUs (0, 1, 2, 3)         |
| git-ollama3-1  | NVIDIA_VISIBLE_DEVICES=all | Can access all GPUs (0, 1, 2, 3)         |

Currently, when an Ollama container needs to use a GPU, it will choose whichever GPU is least busy at that moment. This automatic load balancing works well in many cases but doesn't guarantee that a specific container will always use the same GPU.

## Assigning Specific GPUs to Containers

If you want each Ollama container to use a specific GPU, you can modify the container configuration to restrict each container to one GPU. Here's a recommended assignment:

| Container      | Recommended GPU Setting    | Effect                           |
|----------------|----------------------------|----------------------------------|
| git-ollama0-1  | NVIDIA_VISIBLE_DEVICES=0   | Can only access GPU 0            |
| git-ollama1-1  | NVIDIA_VISIBLE_DEVICES=1   | Can only access GPU 1            |
| git-ollama2-1  | NVIDIA_VISIBLE_DEVICES=2   | Can only access GPU 2            |
| git-ollama3-1  | NVIDIA_VISIBLE_DEVICES=3   | Can only access GPU 3            |

### How to Update GPU Assignments

To update the GPU assignments for your Ollama containers, you would need to recreate each container with the specific GPU assignment. Here's how to do it for each container:

```bash
# For git-ollama0-1 (assigning to GPU 0)
docker stop git-ollama0-1
docker rm git-ollama0-1
docker run -d --name git-ollama0-1 --restart always \
  -v /home/explora/.ollama/models:/root/.ollama/models \
  -v git_ollama0_data:/root/.ollama \
  -p 11434:11434 \
  -e OLLAMA_MODELS=/root/.ollama/models \
  -e OLLAMA_HOST=0.0.0.0:11434 \
  -e NVIDIA_VISIBLE_DEVICES=0 \
  --gpus '"device=0"' \
  ollama/ollama:latest

# For git-ollama1-1 (assigning to GPU 1)
docker stop git-ollama1-1
docker rm git-ollama1-1
docker run -d --name git-ollama1-1 --restart always \
  -v git_ollama1_data:/root/.ollama \
  -v /home/explora/.ollama/models:/root/.ollama/models \
  -p 11435:11434 \
  -e OLLAMA_MODELS=/root/.ollama/models \
  -e OLLAMA_HOST=0.0.0.0:11434 \
  -e NVIDIA_VISIBLE_DEVICES=1 \
  --gpus '"device=1"' \
  ollama/ollama:latest

# For git-ollama2-1 (assigning to GPU 2)
docker stop git-ollama2-1
docker rm git-ollama2-1
docker run -d --name git-ollama2-1 --restart always \
  -v git_ollama2_data:/root/.ollama \
  -v /home/explora/.ollama/models:/root/.ollama/models \
  -p 11436:11434 \
  -e OLLAMA_MODELS=/root/.ollama/models \
  -e OLLAMA_HOST=0.0.0.0:11434 \
  -e NVIDIA_VISIBLE_DEVICES=2 \
  --gpus '"device=2"' \
  ollama/ollama:latest

# For git-ollama3-1 (assigning to GPU 3)
docker stop git-ollama3-1
docker rm git-ollama3-1
docker run -d --name git-ollama3-1 --restart always \
  -v /home/explora/.ollama/models:/root/.ollama/models \
  -v git_ollama3_data:/root/.ollama \
  -p 11437:11434 \
  -e OLLAMA_MODELS=/root/.ollama/models \
  -e OLLAMA_HOST=0.0.0.0:11434 \
  -e NVIDIA_VISIBLE_DEVICES=3 \
  --gpus '"device=3"' \
  ollama/ollama:latest
```

## Benefits of Specific GPU Assignments

Assigning specific GPUs to each Ollama container has several benefits:

1. **Predictable Performance**: Each container has dedicated GPU resources
2. **Resource Isolation**: Heavy usage in one container won't affect others
3. **Easier Monitoring**: You can track which container is using which GPU
4. **Better Memory Management**: Each GPU has its own memory that won't be shared

## Verifying GPU Assignments

After updating the container configurations, you can verify the GPU assignments with:

```bash
for i in {0..3}; do 
  echo "===== CONTAINER git-ollama$i-1 ====="; 
  docker exec git-ollama$i-1 nvidia-smi; 
  echo; 
done
```

This will show which GPUs are visible to each container.

## Updating the Upgrade Script

If you decide to assign specific GPUs to each container, you should update the upgrade script (`~/bin/upgrade-ollama-containers.sh`) to preserve these GPU assignments during future upgrades.
