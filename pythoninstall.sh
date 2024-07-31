#!/bin/bash

# Variables
PYTHON_VERSION="3.11.2"
PYTHON_DOWNLOAD_URL="https://www.python.org/ftp/python/$PYTHON_VERSION/Python-$PYTHON_VERSION.tgz"
MAKE_VERSION="4.3"
MAKE_DOWNLOAD_URL="https://ftp.gnu.org/gnu/make/make-$MAKE_VERSION.tar.gz"

# GCC Variables
GCC_VERSION="12.2.0"
GCC_DOWNLOAD_URL="https://ftp.gnu.org/gnu/gcc/gcc-$GCC_VERSION/gcc-$GCC_VERSION.tar.gz"

# Download and extract GCC (add this section)
echo "Downloading GCC $GCC_VERSION..."
curl -L -O "$GCC_DOWNLOAD_URL"
tar -xf "gcc-$GCC_VERSION.tar.gz"
cd "gcc-$GCC_VERSION"

export PATH="$PATH:/usr/local/bin"
export CC=gcc
export CXX=g++
export CC=/usr/local/bin/gcc
export CXX=/usr/local/bin/g++

# Build and install GCC
./contrib/download_prerequisites
mkdir build
cd build
../configure --disable-multilib
make -j$(nproc)  # May take a while
sudo make install
cd ../../  # Go back up to the script's main directory

pip install cmake==3.23.1   # Example: Install CMake 3.23.1

# Export GCC to PATH
export CC=/usr/local/bin/gcc
export CXX=/usr/local/bin/g++
export PATH=$PATH:/usr/local/bin



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
