# AWS Deployment Guide

## Option 1: EC2 Instance

### Setup

1. **Launch EC2 Instance**
   - AMI: Ubuntu 22.04 LTS
   - Instance type: t2.micro (free tier) or t3.small
   - Security group: Allow ports 22, 8888, 8501

2. **Connect via SSH**
   ```bash
   ssh -i your-key.pem ubuntu@your-ec2-ip
   ```

3. **Install Dependencies**
   ```bash
   sudo apt update
   sudo apt install python3-pip docker.io docker-compose -y
   ```

4. **Clone Repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/Ethic-Latex.git
   cd Ethic-Latex
   ```

5. **Deploy with Docker**
   ```bash
   docker-compose up -d
   ```

6. **Access**
   - Jupyter: http://your-ec2-ip:8888
   - Streamlit: http://your-ec2-ip:8501

### Security

- Use nginx reverse proxy
- Enable SSL with Let's Encrypt
- Set up authentication

## Option 2: ECS (Container Service)

See `deploy/aws/ecs-deploy.sh`

## Option 3: Lambda (Serverless)

For API endpoints only (not full notebooks)

