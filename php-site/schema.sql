-- Phoenix Rebirth / soulReady Platform Database Schema
-- Run this in your Ionos MySQL database

CREATE TABLE IF NOT EXISTS clients (
  id               INT AUTO_INCREMENT PRIMARY KEY,
  email            VARCHAR(255) NOT NULL UNIQUE,
  password_hash    VARCHAR(255) NOT NULL,
  first_name       VARCHAR(100),
  middle_name      VARCHAR(100),
  last_name        VARCHAR(100),
  maiden_name      VARCHAR(100),
  dob              DATE,
  time_of_birth    VARCHAR(20),
  timezone         VARCHAR(100),
  place_of_birth   VARCHAR(255),
  latitude         DECIMAL(9,6),
  longitude        DECIMAL(9,6),
  phone            VARCHAR(50),
  career_field     VARCHAR(255),
  career_expression TEXT,
  intake_complete  TINYINT(1) NOT NULL DEFAULT 0,
  chart_data       LONGTEXT,
  created_at       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS assessments (
  id               INT AUTO_INCREMENT PRIMARY KEY,
  client_id        INT NOT NULL,
  self_love_score  INT NOT NULL DEFAULT 0,
  attachment_style VARCHAR(100),
  attachment_counts TEXT,
  answers          TEXT,
  readiness_score  INT DEFAULT 0,
  completed_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS readings (
  id               INT AUTO_INCREMENT PRIMARY KEY,
  client_id        INT NOT NULL,
  reading_type     VARCHAR(100) NOT NULL,
  status           ENUM('pending','generating','complete','error') NOT NULL DEFAULT 'pending',
  job_id           VARCHAR(36),
  file_name        VARCHAR(255),
  paypal_order_id  VARCHAR(255),
  paypal_capture_id VARCHAR(255),
  paid             TINYINT(1) NOT NULL DEFAULT 0,
  amount_cents     INT DEFAULT 0,
  error_message    TEXT,
  created_at       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE
);
