USE student_mental_health;

-- Base mart view for common analytics use-cases
CREATE OR REPLACE VIEW v_student_mental_health AS
SELECT
    s.student_id,
    su.survey_id,
    su.survey_date,
    su.year_of_study,
    su.cgpa_range,
    su.marital_status,
    su.anxiety_score,
    su.depression_score,
    su.panic_attack_score,
    su.sought_treatment,
    d.age,
    d.gender,
    d.program_of_study
FROM students s
JOIN demographics d ON d.student_id = s.student_id
JOIN surveys su ON su.student_id = s.student_id;

-- KPI by year
SELECT
    year_of_study,
    COUNT(DISTINCT student_id) AS student_count,
    ROUND(AVG(anxiety_score) * 100, 2) AS anxiety_prevalence_pct,
    ROUND(AVG(depression_score) * 100, 2) AS depression_prevalence_pct,
    ROUND(AVG(panic_attack_score) * 100, 2) AS panic_attack_prevalence_pct,
    ROUND(AVG(sought_treatment) * 100, 2) AS treatment_uptake_pct
FROM v_student_mental_health
GROUP BY year_of_study
ORDER BY year_of_study;

-- Segmentation and treatment effectiveness proxy
SELECT
    year_of_study,
    gender,
    COUNT(*) AS n,
    ROUND(AVG(anxiety_score) * 100, 2) AS anxiety_pct,
    ROUND(AVG(CASE WHEN sought_treatment = 1 THEN anxiety_score END) * 100, 2) AS anxiety_if_treated_pct,
    ROUND(AVG(CASE WHEN sought_treatment = 0 THEN anxiety_score END) * 100, 2) AS anxiety_if_not_treated_pct
FROM v_student_mental_health
GROUP BY year_of_study, gender
ORDER BY year_of_study, gender;

-- Rolling and moving averages with window functions
WITH yearly AS (
    SELECT
        year_of_study,
        AVG(anxiety_score) AS avg_anxiety
    FROM v_student_mental_health
    GROUP BY year_of_study
)
SELECT
    year_of_study,
    ROUND(avg_anxiety * 100, 2) AS avg_anxiety_pct,
    ROUND(
        AVG(avg_anxiety) OVER (
            ORDER BY year_of_study
            ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING
        ) * 100,
        2
    ) AS moving_avg_3_point_pct,
    ROUND(
        avg_anxiety * 100
        - LAG(avg_anxiety) OVER (ORDER BY year_of_study) * 100,
        2
    ) AS yoy_change_pct_point
FROM yearly
ORDER BY year_of_study;

-- Ranking high-risk programs
SELECT
    program_of_study,
    COUNT(*) AS responses,
    ROUND(AVG((anxiety_score + depression_score + panic_attack_score) / 3) * 100, 2) AS composite_risk_pct,
    DENSE_RANK() OVER (
        ORDER BY AVG((anxiety_score + depression_score + panic_attack_score) / 3) DESC
    ) AS risk_rank
FROM v_student_mental_health
GROUP BY program_of_study
HAVING COUNT(*) >= 3
ORDER BY risk_rank, program_of_study;

-- Materialized-style aggregate table refresh (run in scheduled job)
CREATE TABLE IF NOT EXISTS agg_yearly_mental_health (
    year_of_study INT PRIMARY KEY,
    student_count INT NOT NULL,
    anxiety_prevalence_pct DECIMAL(5,2) NOT NULL,
    depression_prevalence_pct DECIMAL(5,2) NOT NULL,
    panic_attack_prevalence_pct DECIMAL(5,2) NOT NULL,
    treatment_uptake_pct DECIMAL(5,2) NOT NULL,
    refreshed_at DATETIME NOT NULL
);

REPLACE INTO agg_yearly_mental_health (
    year_of_study,
    student_count,
    anxiety_prevalence_pct,
    depression_prevalence_pct,
    panic_attack_prevalence_pct,
    treatment_uptake_pct,
    refreshed_at
)
SELECT
    year_of_study,
    COUNT(DISTINCT student_id),
    ROUND(AVG(anxiety_score) * 100, 2),
    ROUND(AVG(depression_score) * 100, 2),
    ROUND(AVG(panic_attack_score) * 100, 2),
    ROUND(AVG(sought_treatment) * 100, 2),
    UTC_TIMESTAMP()
FROM v_student_mental_health
GROUP BY year_of_study;

-- Example EXPLAIN usage for optimization review
EXPLAIN FORMAT=TREE
SELECT
    year_of_study,
    COUNT(DISTINCT student_id) AS student_count,
    AVG(anxiety_score) AS anxiety_ratio
FROM v_student_mental_health
GROUP BY year_of_study;