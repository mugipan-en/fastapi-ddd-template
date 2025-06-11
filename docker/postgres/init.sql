-- PostgreSQL initialization script
-- This script runs when the PostgreSQL container is first created

-- Create application database if it doesn't exist
-- Note: This will only run if the database specified in POSTGRES_DB doesn't exist

-- Set up database configuration for better performance
ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements';
ALTER SYSTEM SET log_statement = 'all';
ALTER SYSTEM SET log_duration = on;
ALTER SYSTEM SET log_min_duration_statement = 1000;  -- Log queries taking longer than 1 second

-- Configure connection settings
ALTER SYSTEM SET max_connections = 200;
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;
ALTER SYSTEM SET random_page_cost = 1.1;
ALTER SYSTEM SET effective_io_concurrency = 200;

-- Reload configuration
SELECT pg_reload_conf();

-- Create extensions
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create monitoring user for postgres_exporter
CREATE USER postgres_exporter WITH PASSWORD 'password';
GRANT pg_monitor TO postgres_exporter;
GRANT SELECT ON pg_stat_database TO postgres_exporter;
