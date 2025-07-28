#!/bin/bash

# Get the list of Ollama models, extract names, and sort them in reverse alphabetical order
# tail -n +2 is used to skip the header line from 'ollama list'
models=$(ollama list | awk '{print $1}' | tail -n +2 | sort -r)

echo "Re-pulling models to update timestamps in reverse sorted order:"

for model in $models; do
  echo "Pulling $model..."
  # The 'ollama pull' command updates the last modified timestamp without re-downloading if the model is already present.
  ollama pull "$model"
  sleep 1
done

echo "Ollama models re-pulled. Run 'ollama list' to see the new order."
