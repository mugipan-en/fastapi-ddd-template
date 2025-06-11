# Docker Configuration

This directory contains Docker configurations for running the FastAPI DDD Template in different environments.

## Quick Start

### Development Environment

```bash
# Start development environment
docker-compose -f docker/docker-compose.dev.yml up -d

# Run migrations
docker-compose -f docker/docker-compose.dev.yml exec app alembic upgrade head

# Seed sample data
docker-compose -f docker/docker-compose.dev.yml exec app python scripts/seed_data.py
```

### Production Environment

```bash
# Create production environment file
cp .env.example .env.prod

# Edit .env.prod with production values
# Then start production environment
docker-compose -f docker/docker-compose.prod.yml up -d

# Run migrations
docker-compose -f docker/docker-compose.prod.yml exec app alembic upgrade head
```

## Available Services

### Development Environment

- **FastAPI App**: http://localhost:8000
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379
- **Adminer** (DB Admin): http://localhost:8080
- **Redis Commander**: http://localhost:8081
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)

### Production Environment

- **FastAPI App**: http://localhost:8000 (behind Nginx)
- **Nginx**: http://localhost:80, https://localhost:443
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000
- **Postgres Exporter**: http://localhost:9187
- **Redis Exporter**: http://localhost:9121
- **Node Exporter**: http://localhost:9100

## Configuration Files

- `docker-compose.dev.yml`: Development environment
- `docker-compose.prod.yml`: Production environment
- `nginx/nginx.conf`: Nginx reverse proxy configuration
- `prometheus/prometheus.yml`: Prometheus monitoring configuration
- `grafana/datasources/`: Grafana data source configurations
- `grafana/dashboards/`: Grafana dashboard configurations
- `postgres/init.sql`: PostgreSQL initialization script

## Monitoring Setup

The production environment includes comprehensive monitoring:

- **Prometheus**: Metrics collection
- **Grafana**: Metrics visualization
- **Node Exporter**: System metrics
- **Postgres Exporter**: Database metrics
- **Redis Exporter**: Cache metrics

Default Grafana dashboards are automatically provisioned for FastAPI application metrics.

## Security Considerations

- Change default passwords in production
- Configure SSL certificates for HTTPS
- Restrict access to monitoring endpoints
- Use Docker secrets for sensitive data
- Enable firewall rules for exposed ports
