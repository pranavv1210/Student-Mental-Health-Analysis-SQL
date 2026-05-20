USE student_mental_health;

CREATE INDEX idx_stg_ingestion_ts ON stg_student_mental_health_raw (ingestion_ts);
CREATE INDEX idx_stg_year_treatment ON stg_student_mental_health_raw (year_of_study, sought_treatment);

CREATE INDEX idx_demographics_gender_program ON demographics (gender, program_of_study);

CREATE INDEX idx_surveys_student_date ON surveys (student_id, survey_date);
CREATE INDEX idx_surveys_year_treatment ON surveys (year_of_study, sought_treatment);
CREATE INDEX idx_surveys_year_gender_proxy ON surveys (year_of_study, anxiety_score, depression_score);