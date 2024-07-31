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

# Install required dependencies
sudo yum install -y gcc gcc-c++ openssl-devel bzip2-devel libffi-devel zlib-devel wget make

# Set the CXX environment variable
export CXX=g++

# Download and extract Python source
cd /usr/src
sudo wget https://www.python.org/ftp/python/$PYTHON_VERSION/Python-$PYTHON_VERSION.tgz
sudo tar xzf Python-$PYTHON_VERSION.tgz

# Compile and install Python
cd Python-$PYTHON_VERSION
sudo ./configure --enable-optimizations
sudo make altinstall

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
