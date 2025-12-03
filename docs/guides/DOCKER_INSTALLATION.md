# Docker Installation Guide for Linux

## For Raspberry Pi (ARM Architecture)

### Method 1: Using Docker's Convenience Script (Recommended)

```bash
# Download and run Docker's installation script
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add your user to the docker group (to run docker without sudo)
sudo usermod -aG docker $USER

# Log out and log back in for group changes to take effect
# Or run: newgrp docker

# Verify installation
docker --version
docker run hello-world
```

### Method 2: Using Package Manager (Debian/Ubuntu/Raspberry Pi OS)

```bash
# Update package index
sudo apt-get update

# Install prerequisites
sudo apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Add Docker's official GPG key
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Set up the repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Add your user to the docker group
sudo usermod -aG docker $USER

# Log out and log back in, or run:
newgrp docker

# Verify installation
docker --version
docker run hello-world
```

## For Standard Linux (x86_64/AMD64)

### Ubuntu/Debian

```bash
# Update package index
sudo apt-get update

# Install prerequisites
sudo apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Add Docker's official GPG key
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Set up the repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Add your user to the docker group
sudo usermod -aG docker $USER

# Log out and log back in
newgrp docker

# Verify installation
docker --version
docker run hello-world
```

### CentOS/RHEL/Fedora

```bash
# Install prerequisites
sudo yum install -y yum-utils

# Add Docker repository
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

# Install Docker Engine
sudo yum install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Start Docker
sudo systemctl start docker
sudo systemctl enable docker

# Add your user to the docker group
sudo usermod -aG docker $USER

# Log out and log back in
newgrp docker

# Verify installation
docker --version
docker run hello-world
```

## Install Docker Compose (if not included)

If Docker Compose wasn't installed with the above methods:

```bash
# Download Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Make it executable
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker-compose --version
```

## Post-Installation Steps

1. **Start Docker service:**
   ```bash
   sudo systemctl start docker
   sudo systemctl enable docker  # Enable on boot
   ```

2. **Verify Docker is running:**
   ```bash
   sudo systemctl status docker
   ```

3. **Test Docker:**
   ```bash
   docker run hello-world
   ```

4. **Check Docker Compose:**
   ```bash
   docker-compose --version
   ```

## Troubleshooting

### Permission Denied Errors

If you get "permission denied" errors:
```bash
# Make sure you're in the docker group
groups

# If docker group is not listed, add yourself:
sudo usermod -aG docker $USER

# Log out and log back in, or run:
newgrp docker
```

### Docker Service Not Running

```bash
# Start Docker service
sudo systemctl start docker

# Check status
sudo systemctl status docker
```

### Raspberry Pi Specific Issues

For Raspberry Pi, make sure you're using the ARM version:
- Docker should automatically detect ARM architecture
- If you have issues, check: `uname -m` (should show armv7l or aarch64)

## Next Steps

After installing Docker, you can:
1. Start the Home Assistant Platform: `./start.sh`
2. Or manually: `docker-compose up -d`



