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

# Function to create swap file
create_swap() {
    SWAP_SIZE="2G"
    sudo fallocate -l $SWAP_SIZE /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
}

# Install required dependencies
sudo yum install -y gcc gcc-c++ openssl-devel bzip2-devel libffi-devel zlib-devel wget make

# Set the CXX environment variable
export CXX=g++

# Create swap file to avoid memory issues
create_swap

# Download and extract Python source
cd /usr/src
sudo wget https://www.python.org/ftp/python/$PYTHON_VERSION/Python-$PYTHON_VERSION.tgz
sudo tar xzf Python-$PYTHON_VERSION.tgz

# Compile and install Python with limited jobs to reduce memory usage
cd Python-$PYTHON_VERSION
sudo ./configure --enable-optimizations
sudo make -j2 altinstall  # Limit to 2 concurrent jobs

# Verify the installation
python3.11 --version

# Install pip
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
sudo python3.11 get-pip.py

# Verify pip installation
pip3.11 --version

# Clean up
cd /usr/src
sudo rm -f Python-$PYTHON_VERSION.tgz
sudo rm -f get-pip.py

echo "Python $PYTHON_VERSION and pip have been successfully installed."
