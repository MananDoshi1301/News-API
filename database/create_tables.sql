-- Use db
USE news_api;

-- Create tables
-- CREATE TABLE auth(
--     id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
--     email VARCHAR(255) NOT NULL,
--     password_hash VARCHAR(255) NOT NULL,
--     status ENUM('active', 'inactive', 'locked') DEFAULT 'active',
--     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
--     INDEX(id)
-- );

-- CREATE TABLE authors(
--     id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
--     name VARCHAR(255) NOT NULL UNIQUE
-- );

-- CREATE TABLE categories(
--     id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
--     name VARCHAR(255) NOT NULL UNIQUE
-- );

-- CREATE TABLE news(
--     id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
--     title VARCHAR(255) NOT NULL,
--     source VARCHAR(255) NOT NULL,    
--     date_published DATETIME NOT NULL,
--     popularity INT NOT NULL,
--     author_id INT NOT NULL,
--     category_id INT NOT NULL,
--     FOREIGN KEY (author_id) REFERENCES authors(id),
--     FOREIGN KEY (category_id) REFERENCES categories(id)
--     INDEX (category_id)
--     INDEX (author_id)
--     INDEX (date_published)
--     INDEX (popularity)
-- );


-- CREATE TABLE favourites(
--     news_id INT NOT NULL,
--     user_id INT NOT NULL,
--     FOREIGN KEY (news_id) REFERENCES news(id) ON DELETE CASCADE,
--     FOREIGN KEY (user_id) REFERENCES auth(id) ON DELETE CASCADE,
--     PRIMARY KEY (news_id, user_id)
-- );