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
#create_swap() {
#    SWAP_SIZE="2G"
#    sudo dd if=/dev/zero of=/swapfile bs=1M count=2048
#    sudo chmod 600 /swapfile
#    sudo mkswap /swapfile
#    sudo swapon /swapfile
#    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
#}

# Function to clear the apt cache
clear_cache() {
    sudo apt clean
    sudo rm -rf /var/lib/apt/lists/*
}

# Update package lists
sudo apt update

# Install required dependencies
sudo apt install -y sqlite3 libsqlite3-dev gcc g++ make wget libssl-dev libbz2-dev libffi-dev zlib1g-dev

sudo apt install python3 python3-dev python3-venv
# Set the CXX environment variable
export CXX=g++

# Create swap file to avoid memory issues
#create_swap

# Download and extract Python source
cd /usr/src
sudo wget https://www.python.org/ftp/python/$PYTHON_VERSION/Python-$PYTHON_VERSION.tgz
sudo tar xzf Python-$PYTHON_VERSION.tgz

# Compile and install Python with limited jobs to reduce memory usage
cd Python-$PYTHON_VERSION
sudo ./configure --enable-optimizations
sudo make -j2 altinstall  # Limit to 2 concurrent jobs

# Create symlinks if they don't exist
sudo ln -sf /usr/local/bin/python3.11 /usr/bin/python3.11
sudo ln -sf /usr/local/bin/pip3.11 /usr/bin/pip3.11

# Verify the installation
python3.11 --version

# Install pip
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
sudo python3.11 get-pip.py

# Verify pip installation
pip3.11 --version

# Clean up downloaded files and cache
cd /usr/src
sudo rm -f Python-$PYTHON_VERSION.tgz
sudo rm -f get-pip.py
clear_cache

# Disable and remove the swap file
sudo swapoff /swapfile
sudo rm -f /swapfile
sudo sed -i '/\/swapfile/d' /etc/fstab

echo "Python $PYTHON_VERSION and pip have been successfully installed."
