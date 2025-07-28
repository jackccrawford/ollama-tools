#!/bin/bash
# Script to check the MCP configuration in Windsurf

echo "Checking MCP configuration..."
cat /home/explora/.codeium/windsurf/mcp_config.json

echo -e "\nChecking running MCP servers..."
ps aux | grep mcp | grep -v grep

echo -e "\nChecking Ollama instances..."
for port in 11434 11435 11436 11437; do
  echo -e "\nChecking Ollama instance on port $port..."
  curl -s "http://localhost:$port/api/tags" | grep -o '"name":"[^"]*"' | head -n 5 | cut -d'"' -f4
  echo "..."
done
