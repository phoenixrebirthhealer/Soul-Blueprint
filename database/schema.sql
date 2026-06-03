-- ============================================================
-- Phoenix Rebirth | soulReady
-- MySQL Database Schema
-- Christina Stevens | phoenixrebirth.life
-- ============================================================

SET FOREIGN_KEY_CHECKS = 0;
SET sql_mode = 'STRICT_TRANS_TABLES,NO_ZERO_DATE,NO_ZERO_IN_DATE,ERROR_FOR_DIVISION_BY_ZERO';

-- ============================================================
-- USERS
-- Handles login for both Christina (admin) and clients
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    id                   CHAR(36)        NOT NULL DEFAULT (UUID()),
    email                VARCHAR(255)    NOT NULL UNIQUE,
    password_hash        VARCHAR(255)    NOT NULL,
    role                 ENUM('admin','client') NOT NULL DEFAULT 'client',
    client_id            CHAR(36)        NULL,
    reset_token          VARCHAR(255)    NULL,
    reset_token_expires  DATETIME        NULL,
    created_date         DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login           DATETIME        NULL,
    PRIMARY KEY (id),
    INDEX idx_users_email (email),
    INDEX idx_users_role (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ============================================================
-- CLIENTS
-- Core client record — one per person
-- ============================================================
CREATE TABLE IF NOT EXISTS clients (
    id                   CHAR(36)        NOT NULL DEFAULT (UUID()),
    first_name           VARCHAR(100)    NOT NULL,
    middle_name          VARCHAR(100)    NULL,
    last_name            VARCHAR(100)    NOT NULL,
    maiden_name          VARCHAR(100)    NULL,
    email                VARCHAR(255)    NOT NULL UNIQUE,
    date_of_birth        DATE            NULL,
    time_of_birth        VARCHAR(20)     NULL,
    place_of_birth       VARCHAR(255)    NULL,
    career_field         VARCHAR(255)    NULL,
    career_expression    VARCHAR(255)    NULL,
    created_date         DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_date         DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    INDEX idx_clients_email (email),
    INDEX idx_clients_name (last_name, first_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ============================================================
-- ASSESSMENTS
-- Self-Love quiz results + Hebrew questionnaire responses
-- One per client (update in place)
-- ============================================================
CREATE TABLE IF NOT EXISTS assessments (
    id                     CHAR(36)     NOT NULL DEFAULT (UUID()),
    client_id              CHAR(36)     NOT NULL,
    self_love_score        TINYINT      NULL,
    self_love_result       VARCHAR(100) NULL,
    attachment_style       VARCHAR(100) NULL,
    attachment_scores      JSON         NULL,
    readiness_level        VARCHAR(50)  NULL,
    readiness_score_23     TINYINT      NULL,
    hebrew_questionnaire   JSON         NULL,
    created_date           DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_date           DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    INDEX idx_assessments_client (client_id),
    CONSTRAINT fk_assessments_client FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ============================================================
-- SOUL BLUEPRINT READINGS
-- One per client — stores all reading outputs and unlock flags
-- ============================================================
CREATE TABLE IF NOT EXISTS soul_blueprint_readings (
    id                        CHAR(36)      NOT NULL DEFAULT (UUID()),
    client_id                 CHAR(36)      NOT NULL,
    status                    ENUM('pending_data','queued','generating','complete') NOT NULL DEFAULT 'pending_data',

    -- Calculated data (JSON blobs)
    numerology_data           JSON          NULL,
    hebrew_data               JSON          NULL,
    astrology_data            JSON          NULL,
    human_design_data         JSON          NULL,

    -- Delivered reading files (URLs to GitHub Pages or file storage)
    reading_text              TEXT          NULL,
    map_html_url              TEXT          NULL,
    tier2_neuro               TEXT          NULL,
    tier2_clairs              TEXT          NULL,
    name_frequency_url        TEXT          NULL,
    soulsjourney_url          TEXT          NULL,
    ancestral_url             TEXT          NULL,
    relational_tier1_url      TEXT          NULL,
    relational_tier2_url      TEXT          NULL,
    relational_tier3_url      TEXT          NULL,

    -- Client access unlock flags
    unlocked_tcm_chakra       TINYINT(1)   NOT NULL DEFAULT 0,
    unlocked_tier2            TINYINT(1)   NOT NULL DEFAULT 0,
    unlocked_ancestral        TINYINT(1)   NOT NULL DEFAULT 0,
    unlocked_selflove         TINYINT(1)   NOT NULL DEFAULT 0,
    unlocked_name_frequency   TINYINT(1)   NOT NULL DEFAULT 0,
    unlocked_soulsjourney     TINYINT(1)   NOT NULL DEFAULT 0,
    unlocked_relational_tier1 TINYINT(1)   NOT NULL DEFAULT 0,
    unlocked_relational_tier2 TINYINT(1)   NOT NULL DEFAULT 0,
    unlocked_relational_tier3 TINYINT(1)   NOT NULL DEFAULT 0,
    nd_profile_unlocked       TINYINT(1)   NOT NULL DEFAULT 0,

    created_date              DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_date              DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    INDEX idx_sbr_client (client_id),
    INDEX idx_sbr_status (status),
    CONSTRAINT fk_sbr_client FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ============================================================
-- SERVICES
-- All bookable services with pricing
-- Matches ServiceSelector.jsx exactly
-- ============================================================
CREATE TABLE IF NOT EXISTS services (
    id                CHAR(36)      NOT NULL DEFAULT (UUID()),
    name              VARCHAR(255)  NOT NULL UNIQUE,
    description       VARCHAR(500)  NULL,
    duration_minutes  SMALLINT      NOT NULL,
    price_cents       INT           NOT NULL,
    paypal_link       TEXT          NULL,
    is_active         TINYINT(1)   NOT NULL DEFAULT 1,
    sort_order        TINYINT      NOT NULL DEFAULT 0,
    PRIMARY KEY (id),
    INDEX idx_services_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Seed services from ServiceSelector.jsx
INSERT INTO services (name, description, duration_minutes, price_cents, paypal_link, sort_order) VALUES
('Field Frequency Scan',               'Quick energetic field assessment and clearing',              30, 7500,  'https://www.paypal.com/ncp/payment/EQ6CXD9GQ86GS', 1),
('Rapid Relief',                       'Targeted relief for acute energetic disruptions',            60, 22500, 'https://www.paypal.com/ncp/payment/PUZ86GYBPQ76Y', 2),
('Mild Healing Session',               'Gentle healing for mild energetic imbalances',              60, 27500, 'https://www.paypal.com/ncp/payment/X59AEGA472VTY', 3),
('Chronic Healing Session',            'Deep healing work for chronic patterns and blocks',         90, 47500, 'https://www.paypal.com/ncp/payment/YAKZXK8AZRR2G', 4),
('Guidance Session',                   'Soul-aligned guidance and clarity session',                  60, 45000, 'https://www.paypal.com/ncp/payment/BPQBNMHAN8ELN', 5),
('Sovereign Multidimensional Oracle Reading', 'Full multidimensional oracle and channeled reading', 75, 57500, 'https://www.paypal.com/ncp/payment/R8BSMXF3NZVDW', 6),
('Soul Blueprint Decoder Tier 2',      'Live deep-dive into your Soul Blueprint — Tier 2',         90, 59700, 'https://www.paypal.com/ncp/payment/LDZX3HHBMLLWL', 7);


-- ============================================================
-- BOOKINGS
-- Every session booking — pay via PayPal + schedule, or direct PayPal
-- ============================================================
CREATE TABLE IF NOT EXISTS bookings (
    id                       CHAR(36)     NOT NULL DEFAULT (UUID()),
    client_name              VARCHAR(255) NOT NULL,
    client_email             VARCHAR(255) NOT NULL,
    service_name             VARCHAR(255) NOT NULL,
    service_price_cents      INT          NOT NULL,
    charged_price_cents      INT          NOT NULL,
    ffs_credit_applied       TINYINT(1)  NOT NULL DEFAULT 0,
    slot_utc                 DATETIME     NULL,
    slot_mt                  DATETIME     NULL,
    client_timezone          VARCHAR(100) NULL,
    slot_client_display      VARCHAR(255) NULL,
    slot_mt_display          VARCHAR(255) NULL,
    status                   ENUM('pending_payment','confirmed','cancelled') NOT NULL DEFAULT 'pending_payment',
    paypal_order_id          VARCHAR(255) NULL,
    paypal_capture_id        VARCHAR(255) NULL,
    google_calendar_event_id VARCHAR(255) NULL,
    google_meet_link         TEXT         NULL,
    confirmation_email_sent  TINYINT(1)  NOT NULL DEFAULT 0,
    created_date             DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_date             DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    INDEX idx_bookings_email (client_email),
    INDEX idx_bookings_status (status),
    INDEX idx_bookings_slot (slot_utc),
    INDEX idx_bookings_ffs (client_email, service_name, status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ============================================================
-- AVAILABILITY
-- Christina's schedule management
-- Default schedule auto-generates Mon/Tue/Thu/Fri slots
-- Blocked dates override the default
-- ============================================================
CREATE TABLE IF NOT EXISTS availability_schedule (
    id           CHAR(36)    NOT NULL DEFAULT (UUID()),
    day_of_week  TINYINT     NOT NULL COMMENT '0=Sun 1=Mon 2=Tue 3=Wed 4=Thu 5=Fri 6=Sat',
    start_time   TIME        NOT NULL,
    end_time     TIME        NOT NULL,
    is_active    TINYINT(1) NOT NULL DEFAULT 1,
    PRIMARY KEY (id),
    INDEX idx_schedule_day (day_of_week)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS availability_blocks (
    id          CHAR(36)     NOT NULL DEFAULT (UUID()),
    block_date  DATE         NOT NULL,
    note        VARCHAR(255) NULL,
    created_date DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uk_block_date (block_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Default schedule: Mon Tue Thu Fri, 9am-5pm MT
INSERT INTO availability_schedule (day_of_week, start_time, end_time) VALUES
(1, '09:00:00', '17:00:00'),
(2, '09:00:00', '17:00:00'),
(4, '09:00:00', '17:00:00'),
(5, '09:00:00', '17:00:00');


-- ============================================================
-- MESSAGES
-- Client-Christina messaging system
-- ============================================================
CREATE TABLE IF NOT EXISTS messages (
    id           CHAR(36)                   NOT NULL DEFAULT (UUID()),
    client_id    CHAR(36)                   NOT NULL,
    sender_role  ENUM('client','admin')     NOT NULL,
    content      TEXT                       NOT NULL,
    is_read      TINYINT(1)               NOT NULL DEFAULT 0,
    created_date DATETIME                   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    INDEX idx_messages_client (client_id),
    INDEX idx_messages_unread (client_id, is_read),
    CONSTRAINT fk_messages_client FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ============================================================
-- COURSES
-- 3 courses with lessons and client access tracking
-- ============================================================
CREATE TABLE IF NOT EXISTS courses (
    id           CHAR(36)     NOT NULL DEFAULT (UUID()),
    title        VARCHAR(255) NOT NULL,
    description  TEXT         NULL,
    thumbnail_url TEXT        NULL,
    is_published TINYINT(1)  NOT NULL DEFAULT 0,
    sort_order   TINYINT     NOT NULL DEFAULT 0,
    created_date DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_date DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS course_lessons (
    id           CHAR(36)     NOT NULL DEFAULT (UUID()),
    course_id    CHAR(36)     NOT NULL,
    title        VARCHAR(255) NOT NULL,
    content      LONGTEXT     NULL,
    video_url    TEXT         NULL,
    sort_order   TINYINT     NOT NULL DEFAULT 0,
    is_published TINYINT(1)  NOT NULL DEFAULT 0,
    created_date DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_date DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    INDEX idx_lessons_course (course_id),
    CONSTRAINT fk_lessons_course FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS client_course_access (
    id           CHAR(36)  NOT NULL DEFAULT (UUID()),
    client_id    CHAR(36)  NOT NULL,
    course_id    CHAR(36)  NOT NULL,
    granted_date DATETIME  NOT NULL DEFAULT CURRENT_TIMESTAMP,
    progress     JSON      NULL COMMENT 'Array of completed lesson IDs',
    PRIMARY KEY (id),
    UNIQUE KEY uk_client_course (client_id, course_id),
    CONSTRAINT fk_cca_client FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE,
    CONSTRAINT fk_cca_course FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ============================================================
-- RESOURCES
-- Downloadable resource library with client access control
-- ============================================================
CREATE TABLE IF NOT EXISTS resources (
    id           CHAR(36)     NOT NULL DEFAULT (UUID()),
    title        VARCHAR(255) NOT NULL,
    description  TEXT         NULL,
    file_url     TEXT         NOT NULL,
    file_type    VARCHAR(50)  NULL COMMENT 'pdf, audio, video, image, other',
    category     VARCHAR(100) NULL,
    is_published TINYINT(1)  NOT NULL DEFAULT 0,
    sort_order   SMALLINT    NOT NULL DEFAULT 0,
    created_date DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_date DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    INDEX idx_resources_category (category),
    INDEX idx_resources_published (is_published)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS client_resource_access (
    id           CHAR(36)  NOT NULL DEFAULT (UUID()),
    client_id    CHAR(36)  NOT NULL,
    resource_id  CHAR(36)  NOT NULL,
    granted_date DATETIME  NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uk_client_resource (client_id, resource_id),
    CONSTRAINT fk_cra_client FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE,
    CONSTRAINT fk_cra_resource FOREIGN KEY (resource_id) REFERENCES resources(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


SET FOREIGN_KEY_CHECKS = 1;

-- ============================================================
-- END OF SCHEMA
-- Tables: users, clients, assessments, soul_blueprint_readings,
--         services, bookings, availability_schedule,
--         availability_blocks, messages, courses, course_lessons,
--         client_course_access, resources, client_resource_access
-- ============================================================
