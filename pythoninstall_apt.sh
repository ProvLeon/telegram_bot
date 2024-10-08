#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Define Python version
PYTHON_VERSION="3.11.2"

# Check if sudo is available
if ! command -v sudo &> /dev/null
then
    echo "sudo command not found. Please install sudo and re-run the script."
    exit 1
fi

# Function to clear the apt cache
clear_cache() {
    sudo apt clean
    sudo rm -rf /var/lib/apt/lists/*
}

# Function to check if a command exists
command_exists() {
    command -v "$1" &> /dev/null
}

# Update package lists and install required dependencies
sudo apt update
sudo apt install -y sqlite3 libsqlite3-dev gcc g++ make wget libssl-dev libbz2-dev libffi-dev zlib1g-dev libreadline-dev libncurses5-dev libgdbm-dev libnss3-dev liblzma-dev

# Install Python 3 and virtual environment packages if not already installed
if ! command_exists python3; then
    sudo apt install -y python3
fi

if ! command_exists python3-dev; then
    sudo apt install -y python3-dev
fi

if ! command_exists python3-venv; then
    sudo apt install -y python3-venv
fi

# Set the CXX environment variable
export CXX=g++

# Download and extract Python source
cd /usr/src
sudo wget https://www.python.org/ftp/python/$PYTHON_VERSION/Python-$PYTHON_VERSION.tgz
sudo tar xzf Python-$PYTHON_VERSION.tgz

# Compile and install Python
cd Python-$PYTHON_VERSION
sudo ./configure --enable-optimizations
sudo make -j2 altinstall  # Limit to 2 concurrent jobs

# Create symlinks if they don't exist
sudo ln -sf /usr/local/bin/python3.11 /usr/bin/python3.11
sudo ln -sf /usr/local/bin/pip3.11 /usr/bin/pip3.11

# Verify the installation
python3.11 --version

# Install pip using the official script if not already installed
if ! command_exists pip3.11; then
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    sudo python3.11 get-pip.py
fi

# Verify pip installation
pip3.11 --version

# Clean up downloaded files and cache
cd /usr/src
sudo rm -f Python-$PYTHON_VERSION.tgz
sudo rm -f get-pip.py
clear_cache

echo "Python $PYTHON_VERSION and pip have been successfully installed."
