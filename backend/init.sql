-- Initialize PostgreSQL database for Verified Compliance
-- This script runs when the PostgreSQL container starts

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";

-- Create database if it doesn't exist (handled by POSTGRES_DB env var)
-- Database: verified_compliance
-- User: vc_user
-- Password: vc_password

-- The application will create tables using Alembic migrations
-- This file is for any additional database setup needed
