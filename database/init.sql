-- Create user
-- CREATE USER "root"@"localhost";

-- Create Database
CREATE DATABASE IF NOT EXISTS news_api;

-- Grant privileges
GRANT ALL PRIVILEGES ON news_api.* to 'root'@'localhost';

-- Use db
USE news_api;