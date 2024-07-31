#!/bin/bash

# Variables
PYTHON_VERSION="3.11.2"        # Replace x.x.x with your desired version (e.g., 3.11.2)
PYTHON_DOWNLOAD_URL="https://www.python.org/ftp/python/$PYTHON_VERSION/Python-$PYTHON_VERSION.tgz"

# Download Python
echo "Downloading Python $PYTHON_VERSION..."
curl -L -O "$PYTHON_DOWNLOAD_URL"

# Extract the archive
tar -xf "Python-$PYTHON_VERSION.tgz"

# Navigate into the extracted directory
cd "Python-$PYTHON_VERSION"

# Configure and compile Python
./configure --enable-optimizations
make -j$(nproc)  # Use all available cores for faster compilation

# Install Python (requires sudo for system-wide installation)
sudo make altinstall

# Cleanup
cd ..  # Go back up one directory
rm "Python-$PYTHON_VERSION.tgz"
rm -rf "Python-$PYTHON_VERSION"

echo "Python $PYTHON_VERSION installed successfully!"
