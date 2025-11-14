#!/usr/bin/env bash

# EC2 Setup Script for Password Manager
# Installs Docker, Docker Compose plugin, and AWS CLI on EC2 instance
# Run this script once on a fresh EC2 instance (Ubuntu/Debian/Amazon Linux)

set -euo pipefail

echo "=========================================="
echo "EC2 Setup Script - Password Manager"
echo "=========================================="
echo ""

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
else
    echo "ERROR: Cannot detect OS"
    exit 1
fi

echo "Detected OS: $OS"
echo ""

# ============================================================================
# 1. Install Docker
# ============================================================================
echo "--- Step 1: Installing Docker ---"

if command -v docker &> /dev/null; then
    echo "✓ Docker is already installed"
    docker --version
else
    echo "Installing Docker..."
    
    if [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
        # Update package index
        sudo apt-get update -y
        
        # Install prerequisites
        sudo apt-get install -y \
            ca-certificates \
            curl \
            gnupg \
            lsb-release
        
        # Add Docker's official GPG key
        sudo install -m 0755 -d /etc/apt/keyrings
        curl -fsSL https://download.docker.com/linux/$OS/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
        sudo chmod a+r /etc/apt/keyrings/docker.gpg
        
        # Set up repository
        echo \
          "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/$OS \
          $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
        
        # Install Docker
        sudo apt-get update -y
        sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
        
    elif [ "$OS" = "amzn" ] || [ "$OS" = "amazon" ]; then
        # Amazon Linux 2
        sudo yum update -y
        sudo yum install -y docker
        sudo systemctl start docker
        sudo systemctl enable docker
        sudo usermod -aG docker ec2-user
        
        # Install Docker Compose plugin separately for Amazon Linux
        sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
        
    else
        echo "ERROR: Unsupported OS: $OS"
        echo "Please install Docker manually: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    # Add current user to docker group (if not root)
    if [ "$EUID" -ne 0 ]; then
        sudo usermod -aG docker $USER
        echo "✓ Added $USER to docker group (logout/login required)"
    fi
    
    # Start and enable Docker
    sudo systemctl start docker
    sudo systemctl enable docker
    
    echo "✓ Docker installed successfully"
    docker --version
fi

echo ""

# ============================================================================
# 2. Install Docker Compose (Standalone or Plugin)
# ============================================================================
echo "--- Step 2: Installing Docker Compose ---"

# Check for plugin first
if docker compose version &> /dev/null; then
    echo "✓ Docker Compose plugin is already installed"
    docker compose version
# Check for standalone
elif command -v docker-compose &> /dev/null; then
    echo "✓ Docker Compose (standalone) is already installed"
    docker-compose --version
else
    echo "Installing Docker Compose..."
    
    if [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
        # Try plugin first (Docker 20.10+)
        sudo apt-get install -y docker-compose-plugin
        if docker compose version &> /dev/null; then
            echo "✓ Docker Compose plugin installed"
        else
            # Fallback to standalone
            DOCKER_COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d\" -f4)
            sudo curl -L "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-linux-$(uname -m)" -o /usr/local/bin/docker-compose
            sudo chmod +x /usr/local/bin/docker-compose
            echo "✓ Docker Compose (standalone) installed"
        fi
        
    elif [ "$OS" = "amzn" ] || [ "$OS" = "amazon" ]; then
        # Amazon Linux - install standalone (more reliable)
        DOCKER_COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d\" -f4)
        echo "Installing Docker Compose version ${DOCKER_COMPOSE_VERSION}..."
        sudo curl -L "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-linux-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
        
        # Verify installation
        if docker-compose --version &> /dev/null; then
            echo "✓ Docker Compose (standalone) installed successfully"
            docker-compose --version
        else
            echo "⚠ Warning: Docker Compose installation may have failed"
            echo "Install manually: https://docs.docker.com/compose/install/"
        fi
    else
        echo "ERROR: Unsupported OS for Docker Compose installation"
        echo "Please install Docker Compose manually: https://docs.docker.com/compose/install/"
    fi
fi

echo ""

# ============================================================================
# 3. Install AWS CLI
# ============================================================================
echo "--- Step 3: Installing AWS CLI ---"

if command -v aws &> /dev/null; then
    echo "✓ AWS CLI is already installed"
    aws --version
else
    echo "Installing AWS CLI..."
    
    if [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
        # Install AWS CLI v2
        cd /tmp
        curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
        unzip -q awscliv2.zip
        sudo ./aws/install
        rm -rf aws awscliv2.zip
        
    elif [ "$OS" = "amzn" ] || [ "$OS" = "amazon" ]; then
        # Amazon Linux has AWS CLI v1 by default, upgrade to v2
        cd /tmp
        curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
        unzip -q awscliv2.zip
        sudo ./aws/install --bin-dir /usr/local/bin --install-dir /usr/local/aws-cli
        rm -rf aws awscliv2.zip
        
    else
        echo "ERROR: Unsupported OS for AWS CLI installation"
        echo "Please install AWS CLI manually: https://aws.amazon.com/cli/"
        exit 1
    fi
    
    echo "✓ AWS CLI installed successfully"
    aws --version
fi

echo ""

# ============================================================================
# 4. Create Application Directory
# ============================================================================
echo "--- Step 4: Creating Application Directory ---"

APP_DIR="/opt/password-manager"
sudo mkdir -p "$APP_DIR"
sudo chown $USER:$USER "$APP_DIR"

echo "✓ Created directory: $APP_DIR"
echo ""

# ============================================================================
# 5. Verify IAM Role Attachment
# ============================================================================
echo "--- Step 5: Verifying IAM Role ---"

INSTANCE_ID=$(curl -s http://169.254.169.254/latest/meta-data/instance-id 2>/dev/null || echo "not-ec2")
if [ "$INSTANCE_ID" != "not-ec2" ]; then
    echo "Instance ID: $INSTANCE_ID"
    
    # Check if IAM role is attached
    ROLE_NAME=$(curl -s http://169.254.169.254/latest/meta-data/iam/security-credentials/ 2>/dev/null || echo "")
    if [ -n "$ROLE_NAME" ]; then
        echo "✓ IAM Role attached: $ROLE_NAME"
        
        # Test AWS credentials
        if aws sts get-caller-identity &> /dev/null; then
            echo "✓ AWS credentials working"
            aws sts get-caller-identity
        else
            echo "⚠ Warning: AWS credentials not working. Check IAM role permissions."
        fi
    else
        echo "⚠ Warning: No IAM role detected. Attach IAM role to EC2 instance."
    fi
else
    echo "⚠ Not running on EC2. IAM role check skipped."
fi

echo ""

# ============================================================================
# Summary
# ============================================================================
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. If you were added to docker group, logout and login again"
echo "2. Copy fetch-env.sh to $APP_DIR/"
echo "3. Copy docker-compose.yml (EC2 version) to $APP_DIR/"
echo "4. Run: cd $APP_DIR && ./fetch-env.sh"
echo "5. Run: docker compose up -d"
echo ""
echo "Application directory: $APP_DIR"
echo ""

