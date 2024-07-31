#!/bin/bash

# Variables
PYTHON_VERSION="3.11.2"
PYTHON_DOWNLOAD_URL="https://www.python.org/ftp/python/$PYTHON_VERSION/Python-$PYTHON_VERSION.tgz"

MAKE_VERSION="4.3"          # Choose your desired Make version
MAKE_DOWNLOAD_URL="https://ftp.gnu.org/gnu/make/make-$MAKE_VERSION.tar.gz"

# Install dependencies required for building Make (if not already present)
sudo apt-get update  # Update package list
sudo apt-get install -y build-essential  # Install essential build tools

# Download and extract Make
echo "Downloading Make $MAKE_VERSION..."
curl -L -O "$MAKE_DOWNLOAD_URL"
tar -xf "make-$MAKE_VERSION.tar.gz"
cd "make-$MAKE_VERSION"

# Configure, compile, and install Make
./configure
make -j$(nproc)
sudo make install

# Download and extract Python (same as before)
echo "Downloading Python $PYTHON_VERSION..."
curl -L -O "$PYTHON_DOWNLOAD_URL"
tar -xf "Python-$PYTHON_VERSION.tgz"
cd "Python-$PYTHON_VERSION"

# Configure, compile, and install Python (same as before)
./configure --enable-optimizations
make -j$(nproc)
sudo make altinstall

# Install pip (same as before)
if command -v ensurepip &> /dev/null; then
    echo "Installing pip using ensurepip..."
    python3 -m ensurepip
else
    echo "Installing pip from get-pip.py..."
    curl -L -O https://bootstrap.pypa.io/get-pip.py
    python3 get-pip.py
    rm get-pip.py
fi

# Cleanup
cd ../..  # Go back up two directories
rm "make-$MAKE_VERSION.tar.gz"
rm -rf "make-$MAKE_VERSION"
rm "Python-$PYTHON_VERSION.tgz"
rm -rf "Python-$PYTHON_VERSION"

echo "Python $PYTHON_VERSION, pip, and Make $MAKE_VERSION installed successfully!"
