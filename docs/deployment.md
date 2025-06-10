# Deployment Guide

## Overview

This guide covers deploying the FastAPI DDD Template to various environments including Docker, cloud platforms, and traditional servers.

## Prerequisites

- Docker and Docker Compose
- PostgreSQL database
- Redis instance
- SSL certificate (for production)
- Domain name (for production)

## Environment Variables

### Required Environment Variables

```bash
# Security - MUST be changed in production
SECRET_KEY=your-super-secret-key-change-in-production
JWT_SECRET_KEY=your-jwt-secret-key-change-in-production

# Database
DATABASE_URL=postgresql://user:password@host:5432/dbname

# Redis
REDIS_URL=redis://host:6379

# Application
APP_NAME=FastAPI DDD Template
APP_VERSION=1.0.0
ENVIRONMENT=production
DEBUG=false
```

### Optional Environment Variables

```bash
# JWT Configuration
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=["https://yourdomain.com"]

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=60

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Monitoring
PROMETHEUS_ENABLED=true
METRICS_PORT=9000

# Email
SMTP_HOST=smtp.yourdomain.com
SMTP_PORT=587
SMTP_USER=noreply@yourdomain.com
SMTP_PASSWORD=your-smtp-password
SMTP_FROM_EMAIL=noreply@yourdomain.com
```

## Docker Deployment

### 1. Using Docker Compose (Recommended)

Create a `docker-compose.prod.yml` file:

```yaml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/fastapi_ddd
      - REDIS_URL=redis://redis:6379
      - SECRET_KEY=${SECRET_KEY}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - ENVIRONMENT=production
      - DEBUG=false
    depends_on:
      - db
      - redis
    volumes:
      - ./uploads:/app/uploads
    restart: unless-stopped

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=fastapi_ddd
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./docker/postgres/init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./docker/nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./docker/nginx/ssl:/etc/nginx/ssl
    depends_on:
      - app
    restart: unless-stopped

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./docker/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
      - ./docker/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./docker/grafana/datasources:/etc/grafana/provisioning/datasources
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  prometheus_data:
  grafana_data:
```

Deploy with:
```bash
# Create .env file with production variables
cp .env.example .env.prod

# Build and start services
docker-compose -f docker-compose.prod.yml up -d

# Run migrations
docker-compose -f docker-compose.prod.yml exec app alembic upgrade head
```

### 2. Single Docker Container

```bash
# Build image
docker build -t fastapi-ddd-template .

# Run container
docker run -d \
  --name fastapi-ddd \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/db \
  -e REDIS_URL=redis://host:6379 \
  -e SECRET_KEY=your-secret-key \
  -e JWT_SECRET_KEY=your-jwt-secret \
  fastapi-ddd-template
```

## Cloud Platform Deployment

### AWS ECS

1. **Create ECR repository:**
   ```bash
   aws ecr create-repository --repository-name fastapi-ddd-template
   ```

2. **Build and push image:**
   ```bash
   # Get login token
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-east-1.amazonaws.com

   # Build and tag
   docker build -t fastapi-ddd-template .
   docker tag fastapi-ddd-template:latest 123456789012.dkr.ecr.us-east-1.amazonaws.com/fastapi-ddd-template:latest

   # Push
   docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/fastapi-ddd-template:latest
   ```

3. **Create ECS task definition** (example):
   ```json
   {
     "family": "fastapi-ddd-template",
     "networkMode": "awsvpc",
     "requiresCompatibilities": ["FARGATE"],
     "cpu": "512",
     "memory": "1024",
     "executionRoleArn": "arn:aws:iam::123456789012:role/ecsTaskExecutionRole",
     "containerDefinitions": [
       {
         "name": "fastapi-ddd-template",
         "image": "123456789012.dkr.ecr.us-east-1.amazonaws.com/fastapi-ddd-template:latest",
         "portMappings": [
           {
             "containerPort": 8000,
             "protocol": "tcp"
           }
         ],
         "environment": [
           {
             "name": "DATABASE_URL",
             "value": "postgresql://user:pass@rds-endpoint:5432/db"
           },
           {
             "name": "REDIS_URL",
             "value": "redis://elasticache-endpoint:6379"
           }
         ],
         "secrets": [
           {
             "name": "SECRET_KEY",
             "valueFrom": "arn:aws:ssm:us-east-1:123456789012:parameter/fastapi-ddd/secret-key"
           }
         ],
         "logConfiguration": {
           "logDriver": "awslogs",
           "options": {
             "awslogs-group": "/ecs/fastapi-ddd-template",
             "awslogs-region": "us-east-1",
             "awslogs-stream-prefix": "ecs"
           }
         }
       }
     ]
   }
   ```

### Google Cloud Run

1. **Build and push to Container Registry:**
   ```bash
   # Configure Docker for gcloud
   gcloud auth configure-docker

   # Build and tag
   docker build -t gcr.io/PROJECT_ID/fastapi-ddd-template .

   # Push
   docker push gcr.io/PROJECT_ID/fastapi-ddd-template
   ```

2. **Deploy to Cloud Run:**
   ```bash
   gcloud run deploy fastapi-ddd-template \
     --image gcr.io/PROJECT_ID/fastapi-ddd-template \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars DATABASE_URL=postgresql://... \
     --set-env-vars REDIS_URL=redis://... \
     --memory 1Gi \
     --cpu 1
   ```

### Heroku

1. **Create Heroku app:**
   ```bash
   heroku create your-app-name
   ```

2. **Add buildpack:**
   ```bash
   heroku buildpacks:set heroku/python
   ```

3. **Add addons:**
   ```bash
   heroku addons:create heroku-postgresql:hobby-dev
   heroku addons:create heroku-redis:hobby-dev
   ```

4. **Set environment variables:**
   ```bash
   heroku config:set SECRET_KEY=your-secret-key
   heroku config:set JWT_SECRET_KEY=your-jwt-secret
   heroku config:set ENVIRONMENT=production
   ```

5. **Deploy:**
   ```bash
   git push heroku main
   heroku run alembic upgrade head
   ```

## Traditional Server Deployment

### Using systemd

1. **Install dependencies:**
   ```bash
   sudo apt update
   sudo apt install python3-pip python3-venv nginx postgresql redis-server
   ```

2. **Setup application:**
   ```bash
   # Create user
   sudo useradd -m -s /bin/bash fastapi

   # Setup application
   sudo -u fastapi git clone https://github.com/mugipan-en/fastapi-ddd-template.git /home/fastapi/app
   cd /home/fastapi/app
   sudo -u fastapi python3 -m venv venv
   sudo -u fastapi ./venv/bin/pip install -e ".[dev,lint,security]"
   ```

3. **Create systemd service** (`/etc/systemd/system/fastapi-ddd.service`):
   ```ini
   [Unit]
   Description=FastAPI DDD Template
   After=network.target

   [Service]
   Type=exec
   User=fastapi
   Group=fastapi
   WorkingDirectory=/home/fastapi/app
   Environment=PATH=/home/fastapi/app/venv/bin
   EnvironmentFile=/home/fastapi/app/.env
   ExecStart=/home/fastapi/app/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

4. **Start service:**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable fastapi-ddd
   sudo systemctl start fastapi-ddd
   ```

### Nginx Configuration

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        access_log off;
    }
}
```

## SSL/TLS Setup

### Using Let's Encrypt

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourdomain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## Database Setup

### PostgreSQL

1. **Create database and user:**
   ```sql
   CREATE DATABASE fastapi_ddd;
   CREATE USER fastapi_user WITH PASSWORD 'secure_password';
   GRANT ALL PRIVILEGES ON DATABASE fastapi_ddd TO fastapi_user;
   ```

2. **Run migrations:**
   ```bash
   alembic upgrade head
   ```

3. **Backup strategy:**
   ```bash
   # Create backup script
   #!/bin/bash
   DATE=$(date +%Y%m%d_%H%M%S)
   pg_dump -h localhost -U fastapi_user fastapi_ddd > backup_$DATE.sql

   # Schedule with cron
   0 2 * * * /path/to/backup_script.sh
   ```

## Monitoring and Logging

### Application Monitoring

1. **Prometheus metrics** available at `/metrics`
2. **Health check** available at `/health`
3. **Grafana dashboards** for visualization

### Log Aggregation

```yaml
# docker-compose.logging.yml
version: '3.8'

services:
  elasticsearch:
    image: elasticsearch:7.14.0
    environment:
      - discovery.type=single-node
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data

  logstash:
    image: logstash:7.14.0
    volumes:
      - ./docker/logstash/pipeline:/usr/share/logstash/pipeline

  kibana:
    image: kibana:7.14.0
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200

volumes:
  elasticsearch_data:
```

## Security Considerations

### Production Checklist

- [ ] Change default SECRET_KEY and JWT_SECRET_KEY
- [ ] Use HTTPS in production
- [ ] Set up proper CORS origins
- [ ] Configure rate limiting
- [ ] Set up monitoring and alerting
- [ ] Regular security updates
- [ ] Database connection encryption
- [ ] Secure environment variable handling
- [ ] Regular backups
- [ ] Access logging

### Environment Security

```bash
# Use secrets management
export SECRET_KEY=$(aws ssm get-parameter --name "/app/secret-key" --with-decryption --query "Parameter.Value" --output text)

# Or use Docker secrets
echo "your-secret-key" | docker secret create app_secret_key -
```

## Scaling

### Horizontal Scaling

```yaml
# docker-compose.scale.yml
services:
  app:
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
```

### Load Balancing

```nginx
upstream app_servers {
    server app1:8000;
    server app2:8000;
    server app3:8000;
}

server {
    listen 80;
    location / {
        proxy_pass http://app_servers;
    }
}
```

## Troubleshooting

### Common Issues

1. **Database connection issues:**
   - Check network connectivity
   - Verify credentials
   - Check firewall rules

2. **Memory issues:**
   - Monitor application memory usage
   - Adjust container memory limits
   - Check for memory leaks

3. **Performance issues:**
   - Monitor response times
   - Check database query performance
   - Review application logs

### Health Checks

```bash
# Application health
curl -f http://localhost:8000/health || exit 1

# Database connectivity
curl -f http://localhost:8000/health/db || exit 1

# Detailed status
curl http://localhost:8000/health/detailed
```