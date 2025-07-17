#!/bin/bash

# Function to check if Podman is installed
check_podman() {
    command -v podman >/dev/null 2>&1
    if [[ $? -ne 0 ]]; then
        echo "Podman is not installed. Installing Podman..."
        install_podman
    else
        echo "Podman is already installed."
    fi
}

# Function to install Podman based on OS
install_podman() {
    # Check for macOS or Windows
    if [[ "$OSTYPE" == "darwin"* ]]; then
        install_podman_mac
    elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
        install_podman_windows
    else
        echo "Unsupported OS. This script only supports macOS and Windows."
        exit 1
    fi
}

# Function to install Podman on macOS
install_podman_mac() {
    if ! command -v brew >/dev/null 2>&1; then
        echo "Homebrew is not installed. Please install Homebrew first: https://brew.sh/"
        exit 1
    fi
    echo "Installing Podman on macOS using Homebrew..."
    brew install podman
    if [[ $? -eq 0 ]]; then
        echo "Podman installed successfully on macOS."
    else
        echo "Failed to install Podman on macOS."
        exit 1
    fi
}

# Function to install Podman on Windows (using winget)
install_podman_windows() {
    if ! command -v winget >/dev/null 2>&1; then
        echo "winget is not available. Please install winget first: https://aka.ms/winget"
        exit 1
    fi
    echo "Installing Podman on Windows using winget..."
    winget install --id Podman.Podman
    if [[ $? -eq 0 ]]; then
        echo "Podman installed successfully on Windows."
    else
        echo "Failed to install Podman on Windows."
        exit 1
    fi
}

# Function to check and switch to the master branch, then pull latest changes
check_and_pull_master() {
    # Check if the current directory is a git repository
    if [ ! -d ".git" ]; then
        echo "This is not a git repository. Please navigate to a valid git repository."
        exit 1
    fi
    
    # Get the current branch name
    current_branch=$(git rev-parse --abbrev-ref HEAD)
    
    # Check if the current branch is not 'master'
    if [[ "$current_branch" != "master" ]]; then
        echo "You are on branch '$current_branch'. Switching to 'master' branch..."
        git checkout master
        if [[ $? -ne 0 ]]; then
            echo "Failed to switch to 'master' branch. Exiting."
            exit 1
        fi
    else
        echo "You are already on the 'master' branch."
    fi
    
    # Pull the latest changes from 'master' branch
    echo "Pulling latest changes from 'master' branch..."
    git pull origin master
    if [[ $? -ne 0 ]]; then
        echo "Failed to pull the latest changes from 'master'. Exiting."
        exit 1
    fi
}

# Function to run the Podman commands
run_podman_commands() {
    echo "Starting Podman machine..."
    podman machine start

    echo "Building the image..."
    podman build -t genie -f Containerfile.txt .

    echo "Running the container..."
    podman run -it --rm -p 8501:8501 genie
}

# Main execution
check_podman
check_and_pull_master
run_podman_commands

echo "Podman commands executed successfully."
