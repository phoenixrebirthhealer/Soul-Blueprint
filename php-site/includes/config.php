<?php
// -------------------------------------------------------
// Fill in your Ionos MySQL credentials here
// Ionos: Hosting > Databases > pick your DB > Details
// -------------------------------------------------------
define('DB_HOST', 'localhost');       // usually localhost on Ionos
define('DB_NAME', 'your_db_name');    // your database name
define('DB_USER', 'your_db_user');    // your database username
define('DB_PASS', 'your_db_password'); // your database password
define('DB_CHARSET', 'utf8mb4');

define('RAILWAY_API', 'https://soul-blueprint-production.up.railway.app');
define('SITE_URL', 'https://phoenixrebirth.life');
define('READINGS_DIR', __DIR__ . '/../readings/');
define('READINGS_URL', SITE_URL . '/readings/');
