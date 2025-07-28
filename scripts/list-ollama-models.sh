#!/bin/bash
# Script to list all available Ollama models
# Usage: list-ollama-models.sh [instance_port]
# Default port is 11434 if not specified

PORT=${1:-11434}

echo "Listing Ollama models on port $PORT..."
curl -s "http://localhost:$PORT/api/tags" | grep -o '"name":"[^"]*"' | cut -d'"' -f4
