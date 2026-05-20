from __future__ import annotations

from datetime import datetime

import mysql.connector
import pandas as pd

from config.logger import get_logger
from config.settings import settings
from etl.extract import extract_csv
from etl.transform import transform

logger = get_logger("etl.load", settings.log_level)


def get_connection() -> mysql.connector.MySQLConnection:
    return mysql.connector.connect(
        host=settings.mysql_host,
        port=settings.mysql_port,
        user=settings.mysql_user,
        password=settings.mysql_password,
        database=settings.mysql_database,
    )


def _chunked(iterable: list[tuple], size: int) -> list[list[tuple]]:
    return [iterable[i : i + size] for i in range(0, len(iterable), size)]


def run_load() -> None:
    started_at = datetime.utcnow()
    logger.info("ETL run started")

    raw_df = extract_csv()
    clean_df = transform(raw_df)

    cnx = get_connection()
    cursor = cnx.cursor(dictionary=True)

    try:
        cursor.execute("INSERT INTO etl_run_audit (started_at, status) VALUES (UTC_TIMESTAMP(), 'RUNNING')")
        etl_run_id = cursor.lastrowid
        cnx.commit()

        stage_rows = [
            (
                row["record_hash"],
                row["timestamp"].to_pydatetime(),
                row["gender"],
                int(row["age"]),
                row["course"],
                int(row["year_of_study"]),
                row["cgpa_range"],
                row["marital_status"],
                int(row["depression"]),
                int(row["anxiety"]),
                int(row["panic_attack"]),
                int(row["sought_treatment"]),
            )
            for _, row in clean_df.iterrows()
        ]

        insert_stage_sql = """
        INSERT INTO stg_student_mental_health_raw (
            record_hash, survey_timestamp, gender, age, course, year_of_study, cgpa_range,
            marital_status, depression_score, anxiety_score, panic_attack_score, sought_treatment
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            survey_timestamp = VALUES(survey_timestamp),
            gender = VALUES(gender),
            age = VALUES(age),
            course = VALUES(course),
            year_of_study = VALUES(year_of_study),
            cgpa_range = VALUES(cgpa_range),
            marital_status = VALUES(marital_status),
            depression_score = VALUES(depression_score),
            anxiety_score = VALUES(anxiety_score),
            panic_attack_score = VALUES(panic_attack_score),
            sought_treatment = VALUES(sought_treatment)
        """

        for chunk in _chunked(stage_rows, settings.batch_size):
            cursor.executemany(insert_stage_sql, chunk)
        cnx.commit()
        logger.info("Staging upsert complete: %s rows", len(stage_rows))

        cursor.execute(
            """
            INSERT IGNORE INTO students (record_hash)
            SELECT record_hash FROM stg_student_mental_health_raw
            """
        )

        cursor.execute(
            """
            INSERT INTO demographics (student_id, age, gender, program_of_study)
            SELECT s.student_id, stg.age, stg.gender, stg.course
            FROM stg_student_mental_health_raw stg
            JOIN students s ON s.record_hash = stg.record_hash
            ON DUPLICATE KEY UPDATE
                age = VALUES(age),
                gender = VALUES(gender),
                program_of_study = VALUES(program_of_study)
            """
        )

        cursor.execute(
            """
            INSERT INTO surveys (
                student_id, survey_date, year_of_study, cgpa_range,
                marital_status, anxiety_score, depression_score,
                panic_attack_score, sought_treatment
            )
            SELECT
                s.student_id,
                stg.survey_timestamp,
                stg.year_of_study,
                stg.cgpa_range,
                stg.marital_status,
                stg.anxiety_score,
                stg.depression_score,
                stg.panic_attack_score,
                stg.sought_treatment
            FROM stg_student_mental_health_raw stg
            JOIN students s ON s.record_hash = stg.record_hash
            LEFT JOIN surveys su
              ON su.student_id = s.student_id
             AND su.survey_date = stg.survey_timestamp
            WHERE su.survey_id IS NULL
            """
        )

        cnx.commit()

        cursor.execute(
            """
            UPDATE etl_run_audit
            SET completed_at = UTC_TIMESTAMP(), status = 'SUCCESS', source_rows = %s, transformed_rows = %s
            WHERE etl_run_id = %s
            """,
            (len(raw_df), len(clean_df), etl_run_id),
        )
        cnx.commit()

        duration = (datetime.utcnow() - started_at).total_seconds()
        logger.info("ETL run succeeded in %.2f sec", duration)

    except Exception as exc:
        cnx.rollback()
        logger.exception("ETL run failed: %s", exc)
        try:
            cursor.execute(
                """
                UPDATE etl_run_audit
                SET completed_at = UTC_TIMESTAMP(), status = 'FAILED', error_message = %s
                WHERE etl_run_id = (SELECT MAX(etl_run_id) FROM etl_run_audit)
                """,
                (str(exc)[:500],),
            )
            cnx.commit()
        except Exception:
            logger.exception("Failed to persist failure metadata")
        raise
    finally:
        cursor.close()
        cnx.close()


if __name__ == "__main__":
    run_load()