# Create a directory for building
mkdir -p ~/build
cd ~/build

# Download SQLite source
curl -O https://www.sqlite.org/2024/sqlite-autoconf-3390200.tar.gz

# Verify the download
file sqlite-autoconf-3390200.tar.gz

# Extract the tarball
tar -xzf sqlite-autoconf-3390200.tar.gz

# Navigate into the directory
cd sqlite-autoconf-3390200

# Configure, build, and install
./configure --prefix=/usr/local
make -j$(nproc)
sudo make install

# Clean up
cd ~/build
rm -rf sqlite-autoconf-3390200*


# Download and extract Python source
cd ~/build
curl -O https://www.python.org/ftp/python/3.11.2/Python-3.11.2.tgz
tar -xzf Python-3.11.2.tgz
cd Python-3.11.2

# Configure Python with SQLite support
./configure --enable-optimizations --with-openssl=/usr/local
make -j$(nproc)
sudo make altinstall

# Create symlinks if needed
sudo ln -sf /usr/local/bin/python3.11 /usr/bin/python3.11
sudo ln -sf /usr/local/bin/pip3.11 /usr/bin/pip3.11

# Verify the installation
python3.11 --version
pip3.11 --version

# Clean up
cd ~
rm -rf ~/build
