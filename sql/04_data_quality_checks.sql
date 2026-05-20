USE student_mental_health;

-- 1. Null checks
SELECT 'null_gender' AS check_name, COUNT(*) AS issue_count
FROM stg_student_mental_health_raw
WHERE gender IS NULL OR TRIM(gender) = '';

SELECT 'null_course' AS check_name, COUNT(*) AS issue_count
FROM stg_student_mental_health_raw
WHERE course IS NULL OR TRIM(course) = '';

-- 2. Domain checks for binary scores
SELECT 'invalid_binary_values' AS check_name, COUNT(*) AS issue_count
FROM stg_student_mental_health_raw
WHERE depression_score NOT IN (0,1)
   OR anxiety_score NOT IN (0,1)
   OR panic_attack_score NOT IN (0,1)
   OR sought_treatment NOT IN (0,1);

-- 3. Referential integrity checks
SELECT 'orphan_demographics' AS check_name, COUNT(*) AS issue_count
FROM demographics d
LEFT JOIN students s ON s.student_id = d.student_id
WHERE s.student_id IS NULL;

SELECT 'orphan_surveys' AS check_name, COUNT(*) AS issue_count
FROM surveys su
LEFT JOIN students s ON s.student_id = su.student_id
WHERE s.student_id IS NULL;

-- 4. Freshness check (data latency in hours)
SELECT
    'freshness_hours' AS check_name,
    TIMESTAMPDIFF(HOUR, MAX(ingestion_ts), UTC_TIMESTAMP()) AS metric_value
FROM stg_student_mental_health_raw;

-- 5. Duplicate survey grain check (should be zero because of unique key)
SELECT
    'duplicate_student_survey_datetime' AS check_name,
    COUNT(*) AS issue_count
FROM (
    SELECT student_id, survey_date, COUNT(*) AS c
    FROM surveys
    GROUP BY student_id, survey_date
    HAVING COUNT(*) > 1
) t;