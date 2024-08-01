#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Define versions
PYTHON_VERSION="3.11.2"
GCC_VERSION="12.2.0"
MAKE_VERSION="4.4"
OPENSSL_VERSION="3.0.8"

# Function to download and extract a tarball
download_and_extract() {
    local url=$1
    local tarball=$(basename "$url")
    curl -O "$url"
    tar -xf "$tarball"
    rm -f "$tarball"
}

# Create a directory for building
mkdir -p ~/build
cd ~/build

# Install GCC
download_and_extract "https://ftp.gnu.org/gnu/gcc/gcc-${GCC_VERSION}/gcc-${GCC_VERSION}.tar.gz"
cd gcc-${GCC_VERSION}
./contrib/download_prerequisites
mkdir build && cd build
../configure --enable-languages=c,c++ --disable-multilib
make -j$(nproc)
sudo make install
cd ~/build
rm -rf gcc-${GCC_VERSION}

# Install Make
download_and_extract "https://ftp.gnu.org/gnu/make/make-${MAKE_VERSION}.tar.gz"
cd make-${MAKE_VERSION}
./configure
make -j$(nproc)
sudo make install
cd ~/build
rm -rf make-${MAKE_VERSION}

# Install OpenSSL
download_and_extract "https://www.openssl.org/source/openssl-${OPENSSL_VERSION}.tar.gz"
cd openssl-${OPENSSL_VERSION}
./config
make -j$(nproc)
sudo make install
cd ~/build
rm -rf openssl-${OPENSSL_VERSION}

# Install required libraries
mkdir -p ~/build-libs
cd ~/build-libs

# Install zlib
download_and_extract "https://zlib.net/zlib-1.2.13.tar.gz"
cd zlib-1.2.13
./configure
make -j$(nproc)
sudo make install
cd ~/build-libs
rm -rf zlib-1.2.13

# Install libffi
download_and_extract "https://github.com/libffi/libffi/releases/download/v3.4.4/libffi-3.4.4.tar.gz"
cd libffi-3.4.4
./configure --prefix=/usr/local
make -j$(nproc)
sudo make install
cd ~/build-libs
rm -rf libffi-3.4.4

# Install Python
cd ~/build
download_and_extract "https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tgz"
cd Python-${PYTHON_VERSION}
./configure --enable-optimizations --with-openssl=/usr/local/ssl
make -j$(nproc)
sudo make altinstall

# Create symlinks if they don't exist
sudo ln -sf /usr/local/bin/python3.11 /usr/bin/python3.11
sudo ln -sf /usr/local/bin/pip3.11 /usr/bin/pip3.11

# Verify the installation
python3.11 --version
pip3.11 --version

# Clean up
cd ~
rm -rf ~/build ~/build-libs

echo "Python $PYTHON_VERSION and pip have been successfully installed with all dependencies."
