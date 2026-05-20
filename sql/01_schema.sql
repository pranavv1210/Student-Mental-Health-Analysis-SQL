-- Core schema for production-style analytics pipeline
CREATE DATABASE IF NOT EXISTS student_mental_health;
USE student_mental_health;

CREATE TABLE IF NOT EXISTS etl_run_audit (
    etl_run_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    started_at DATETIME NOT NULL,
    completed_at DATETIME NULL,
    status VARCHAR(20) NOT NULL,
    source_rows INT NULL,
    transformed_rows INT NULL,
    error_message VARCHAR(500) NULL
);

CREATE TABLE IF NOT EXISTS stg_student_mental_health_raw (
    stg_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    record_hash CHAR(64) NOT NULL UNIQUE,
    survey_timestamp DATETIME NOT NULL,
    gender VARCHAR(20) NOT NULL,
    age INT NOT NULL,
    course VARCHAR(100) NOT NULL,
    year_of_study INT NOT NULL,
    cgpa_range VARCHAR(50) NOT NULL,
    marital_status VARCHAR(20) NOT NULL,
    depression_score TINYINT NOT NULL,
    anxiety_score TINYINT NOT NULL,
    panic_attack_score TINYINT NOT NULL,
    sought_treatment TINYINT NOT NULL,
    ingestion_ts DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (age BETWEEN 15 AND 60),
    CHECK (year_of_study BETWEEN 1 AND 8),
    CHECK (depression_score IN (0,1)),
    CHECK (anxiety_score IN (0,1)),
    CHECK (panic_attack_score IN (0,1)),
    CHECK (sought_treatment IN (0,1))
);

CREATE TABLE IF NOT EXISTS students (
    student_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    record_hash CHAR(64) NOT NULL UNIQUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS demographics (
    student_id BIGINT PRIMARY KEY,
    age INT NOT NULL,
    gender VARCHAR(20) NOT NULL,
    program_of_study VARCHAR(100) NOT NULL,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CHECK (age BETWEEN 15 AND 60),
    CONSTRAINT fk_demographics_student FOREIGN KEY (student_id)
        REFERENCES students(student_id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS surveys (
    survey_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    student_id BIGINT NOT NULL,
    survey_date DATETIME NOT NULL,
    year_of_study INT NOT NULL,
    cgpa_range VARCHAR(50) NOT NULL,
    marital_status VARCHAR(20) NOT NULL,
    anxiety_score TINYINT NOT NULL,
    depression_score TINYINT NOT NULL,
    panic_attack_score TINYINT NOT NULL,
    sought_treatment TINYINT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_student_survey (student_id, survey_date),
    CHECK (year_of_study BETWEEN 1 AND 8),
    CHECK (anxiety_score IN (0,1)),
    CHECK (depression_score IN (0,1)),
    CHECK (panic_attack_score IN (0,1)),
    CHECK (sought_treatment IN (0,1)),
    CONSTRAINT fk_surveys_student FOREIGN KEY (student_id)
        REFERENCES students(student_id)
        ON DELETE CASCADE ON UPDATE CASCADE
);