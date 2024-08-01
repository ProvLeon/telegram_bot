mkdir -p ~/build
cd ~/build

# Download and build SQLite
curl -O https://www.sqlite.org/2024/sqlite-autoconf-3390200.tar.gz
tar -xzf sqlite-autoconf-3390200.tar.gz
cd sqlite-autoconf-3390200
./configure --prefix=/usr/local
make
sudo make install
cd ~/build
rm -rf sqlite-autoconf-3390200

# create or modify /etc/ld.so.conf to include this directory
echo "/usr/local/lib" | sudo tee -a /etc/ld.so.conf
sudo ldconfig


# Rebuild Python if necessary
cd ~/build
curl -O https://www.python.org/ftp/python/3.11.2/Python-3.11.2.tgz
tar -xzf Python-3.11.2.tgz
cd Python-3.11.2

# Configure Python with the path to SQLite and OpenSSL
./configure --enable-optimizations --with-openssl=/usr/local --enable-loadable-sqlite-extensions
make -j$(nproc)
sudo make altinstall

# Create symlinks if needed
sudo ln -sf /usr/local/bin/python3.11 /usr/bin/python3.11
sudo ln -sf /usr/local/bin/pip3.11 /usr/bin/pip3.11
