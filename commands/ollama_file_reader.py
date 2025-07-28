#!/usr/bin/env python3
"""
Ollama File Reader - A tool that allows Ollama models to read files using function calling.

This script provides a chat interface where you can ask questions about files,
and the model will use function calling to read the file contents before responding.

Usage:
  ./ollama_file_reader.py [--model MODEL_NAME]

Examples:
  ./ollama_file_reader.py --model llama3.1
  
  Then you can ask:
  "What does the file /path/to/your/file.txt contain?"
  "Can you summarize the content of /path/to/your/other_file.md?"
  "Read the file at /path/to/your/file.txt and tell me what it's about."
  "List the files in /path/to/your/directory directory."
"""

import argparse
import json
import os
import sys
from pathlib import Path

# Try to import ollama, with a helpful error message if it's not installed
try:
    import ollama
except ImportError:
    print("Error: The 'ollama' package is not installed.")
    print("Please install it with: pip install ollama")
    sys.exit(1)

# Define file operation functions
def read_file_content(file_path: str) -> str:
    """
    Reads the content of a file and returns it as a string.
    
    Args:
        file_path: The path to the file to read
        
    Returns:
        The content of the file as a string
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        return f"Error: File not found at {file_path}"
    except PermissionError:
        return f"Error: Permission denied when trying to read {file_path}"
    except UnicodeDecodeError:
        return f"Error: Unable to decode file {file_path}. It might be a binary file."
    except Exception as e:
        return f"Error reading file {file_path}: {str(e)}"


def list_directory_contents(directory_path: str) -> str:
    """
    Lists the contents of a directory.
    
    Args:
        directory_path: The path to the directory to list
        
    Returns:
        A string containing the directory contents
    """
    try:
        items = os.listdir(directory_path)
        files = []
        directories = []
        
        for item in items:
            full_path = os.path.join(directory_path, item)
            if os.path.isdir(full_path):
                directories.append(f"{item}/")
            else:
                files.append(item)
        
        output = []
        if directories:
            output.append("Directories:")
            for d in sorted(directories):
                output.append(f"  - {d}")
        
        if files:
            output.append("Files:")
            for f in sorted(files):
                output.append(f"  - {f}")
        
        if not output:
            return f"The directory {directory_path} is empty."
        
        return f"Contents of {directory_path}:\n" + "\n".join(output)
    except FileNotFoundError:
        return f"Error: Directory not found at {directory_path}"
    except PermissionError:
        return f"Error: Permission denied when trying to list {directory_path}"
    except Exception as e:
        return f"Error listing directory {directory_path}: {str(e)}"


def file_info(file_path: str) -> str:
    """
    Get information about a file such as size, modification time, and type.
    
    Args:
        file_path: The path to the file to get information about
        
    Returns:
        A string containing information about the file
    """
    try:
        if not os.path.exists(file_path):
            return f"Error: File/directory not found at {file_path}"
        
        info = []
        stats = os.stat(file_path)
        
        # File type
        if os.path.isdir(file_path):
            info.append(f"Type: Directory")
        elif os.path.islink(file_path):
            info.append(f"Type: Symbolic Link to {os.readlink(file_path)}")
        else:
            info.append(f"Type: File")
        
        # Size
        if not os.path.isdir(file_path):
            size_bytes = stats.st_size
            if size_bytes < 1024:
                size_str = f"{size_bytes} bytes"
            elif size_bytes < 1024 * 1024:
                size_str = f"{size_bytes / 1024:.2f} KB"
            elif size_bytes < 1024 * 1024 * 1024:
                size_str = f"{size_bytes / (1024 * 1024):.2f} MB"
            else:
                size_str = f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"
            
            info.append(f"Size: {size_str}")
        
        # Modification time
        mod_time = os.path.getmtime(file_path)
        info.append(f"Last modified: {os.path.getmtime(file_path)}")
        
        # Access permissions
        permissions = ""
        if os.access(file_path, os.R_OK):
            permissions += "r"
        else:
            permissions += "-"
        
        if os.access(file_path, os.W_OK):
            permissions += "w"
        else:
            permissions += "-"
        
        if os.access(file_path, os.X_OK):
            permissions += "x"
        else:
            permissions += "-"
        
        info.append(f"Permissions: {permissions}")
        
        return f"Information for {file_path}:\n" + "\n".join(info)
    except Exception as e:
        return f"Error getting information for {file_path}: {str(e)}"


def get_file_extension(file_path: str) -> str:
    """
    Get the extension of a file.
    
    Args:
        file_path: The path to the file
        
    Returns:
        The file extension (without the dot)
    """
    return os.path.splitext(file_path)[1][1:]


# Main chat function with model
def chat_with_model(model_name):
    # Define the tools in OpenAI format for Ollama
    tools = [
        {
            "type": "function",
            "function": {
                "name": "read_file_content",
                "description": "Read the content of a file and return it as a string",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "The path to the file to read"
                        }
                    },
                    "required": ["file_path"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "list_directory_contents",
                "description": "List the contents of a directory",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "directory_path": {
                            "type": "string",
                            "description": "The path to the directory to list"
                        }
                    },
                    "required": ["directory_path"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "file_info",
                "description": "Get information about a file or directory such as size, modification time, and type",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "The path to the file or directory to get information about"
                        }
                    },
                    "required": ["file_path"]
                }
            }
        }
    ]
    
    # Define functions that can be called by the model
    available_functions = {
        "read_file_content": read_file_content,
        "list_directory_contents": list_directory_contents,
        "file_info": file_info
    }
    
    # System prompt to instruct the model on its capabilities
    system_prompt = """You are an AI assistant with the ability to read files and list directory contents.
You can assist users by reading files and providing information about their content.

When a user asks about a file or its contents, you should use the appropriate function:
- read_file_content: To read the contents of a file
- list_directory_contents: To list files and directories in a given directory
- file_info: To get information about a file or directory

Do not attempt to write to files as you do not have permission to do so.
Always help users understand the content of files they ask about."""
    
    print(f"Chat with {model_name} about files. Type 'exit' to quit.")
    print("Example questions:")
    print("  - What's in the file /path/to/your/file.txt?")
    print("  - List the files in /path/to/your/directory directory")
    print("  - Tell me about the file /path/to/your/other_file.md")
    print()
    
    # Initialize conversation history
    messages = [{"role": "system", "content": system_prompt}]
    
    while True:
        # Get user input
        user_input = input("\nYou: ")
        if user_input.lower() == "exit":
            break
        
        # Add user message to conversation history
        messages.append({"role": "user", "content": user_input})
        
        try:
            # Get model response
            response = ollama.chat(
                model=model_name,
                messages=messages,
                tools=tools,
                stream=False
            )
            
            # Add model response to conversation history
            messages.append(response["message"])
            
            # Check for tool calls
            tool_calls = response["message"].get("tool_calls", [])
            
            if tool_calls:
                print("\n(Model is using tools to help answer your question...)")
                
                # Process each tool call
                for tool_call in tool_calls:
                    function_name = tool_call["function"]["name"]
                    
                    if function_name in available_functions:
                        # Parse function arguments
                        try:
                            function_args = json.loads(tool_call["function"]["arguments"])
                        except json.JSONDecodeError:
                            print(f"Error: Could not parse arguments for {function_name}")
                            continue
                        
                        # Call the function with the provided arguments
                        function_to_call = available_functions[function_name]
                        function_response = function_to_call(**function_args)
                        
                        # Log tool call for debugging (optional)
                        print(f"(Using {function_name} on {function_args})")
                        
                        # Add tool response to conversation history
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call["id"],
                            "name": function_name, 
                            "content": function_response
                        })
                
                # Get final response with tool results incorporated
                final_response = ollama.chat(
                    model=model_name,
                    messages=messages,
                    stream=False
                )
                
                # Update conversation history with final response
                messages.append(final_response["message"])
                
                # Print the final response
                print(f"\nAI: {final_response['message']['content']}")
            else:
                # Print the initial response (no tool calls)
                print(f"\nAI: {response['message']['content']}")
        
        except Exception as e:
            print(f"\nError: {str(e)}")
            print("Try asking a different question.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chat with an Ollama model about files")
    parser.add_argument("--model", type=str, default="llama3.1",
                        help="The Ollama model to use (default: llama3.1)")
    args = parser.parse_args()
    
    chat_with_model(args.model)
