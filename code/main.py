"""
Learner Assessment & Resource Management System (LEARMS)
Module: code.main
Description: Core pipeline engine responsible for data parsing, validation,
             quality audit sampling, database persistence, and transaction logging.
Author: Mohammed Wael (Junior Solutions Consultant)
Organization: Sprints
"""

import os
import sys
import csv
import math
import time
import sqlite3
import logging
import argparse
from datetime import datetime, timezone
from typing import Dict, Any, Tuple, Optional, List

# Ensure relative imports resolve whether executed directly or as a package
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from code.models import Learner, Instructor, User


# =====================================================================
# Telemetry & Activity Logging Configuration
# =====================================================================

def configure_logger(log_file_path: str) -> logging.Logger:
    """
    Configure a dedicated logger that appends application events and database
    transaction summaries to an external log file, while also mirroring
    informational notices to stdout.

    Args:
        log_file_path (str): Filesystem path to the destination log file.

    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger("LEARMS_Engine")
    logger.setLevel(logging.INFO)

    # Prevent duplicate handlers on repeated invocations
    if logger.hasHandlers():
        logger.handlers.clear()

    log_format = logging.Formatter(
        fmt="[%(asctime)s] [%(levelname)s] [%(module)s:%(lineno)d] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 1. File Handler (Appends events to application_activity.log)
    try:
        log_dir = os.path.dirname(os.path.abspath(log_file_path))
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        file_handler = logging.FileHandler(log_file_path, mode="a", encoding="utf-8")
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(log_format)
        logger.addHandler(file_handler)
    except (IOError, PermissionError, OSError) as err:
        err_msg = (
            f"Critical Logging Failure: Mandatory application activity log cannot be created "
            f"or opened for appending at '{log_file_path}'. Cause: {err}"
        )
        print(f"[FATAL ERROR] {err_msg}", file=sys.stderr)
        raise RuntimeError(err_msg) from err

    # 2. Console Handler for real-time CLI visibility
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(log_format)
    logger.addHandler(console_handler)

    return logger


# =====================================================================
# Database Layer (SQLite Normalized Relational Engine)
# =====================================================================

class DatabaseManager:
    """
    Manages SQLite database connections, schema provisioning, normalized
    table operations, and transaction integrity.
    """

    def __init__(self, db_path: str, logger: logging.Logger) -> None:
        """
        Initialize the DatabaseManager with path and logger.

        Args:
            db_path: Path to sprints_learners.db file.
            logger: Active logger instance.
        """
        self.db_path = os.path.abspath(db_path)
        self.logger = logger
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    def get_connection(self) -> sqlite3.Connection:
        """
        Open and return a SQLite database connection with foreign key enforcement.

        Returns:
            sqlite3.Connection: Database connection object.

        Raises:
            sqlite3.OperationalError: If connection cannot be established.
        """
        try:
            conn = sqlite3.connect(self.db_path, timeout=30.0)
            # Enforce foreign key constraints strictly
            conn.execute("PRAGMA foreign_keys = ON;")
            conn.row_factory = sqlite3.Row
            return conn
        except sqlite3.Error as err:
            self.logger.critical("Failed to connect to SQLite database at '%s': %s", self.db_path, err)
            raise

    def initialize_schema(self) -> None:
        """
        Construct normalized relational tables for Cohorts and Learners.
        Guarantees Third Normal Form (3NF) relational layout with foreign keys.
        Includes an automated migration step to deduplicate any legacy audit records
        prior to enforcing the unique constraint index on (event_type, learner_id).
        """
        schema_tables_sql = """
        -- 1. Cohorts Table (Parent entity)
        CREATE TABLE IF NOT EXISTS cohorts (
            cohort_id INTEGER PRIMARY KEY AUTOINCREMENT,
            cohort_name TEXT NOT NULL UNIQUE,
            program_track TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- 2. Learners Table (Child entity referencing cohorts)
        CREATE TABLE IF NOT EXISTS learners (
            learner_id TEXT PRIMARY KEY,
            full_name TEXT NOT NULL,
            cohort_id INTEGER NOT NULL,
            assessment_score REAL NOT NULL CHECK(assessment_score >= 0.0 AND assessment_score <= 100.0),
            enrollment_status TEXT NOT NULL CHECK(enrollment_status IN ('Active', 'Graduated', 'Dropped')),
            is_audited INTEGER NOT NULL DEFAULT 0 CHECK(is_audited IN (0, 1)),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (cohort_id) REFERENCES cohorts (cohort_id) ON DELETE RESTRICT ON UPDATE CASCADE
        );

        -- 3. System Audit Log Table for historical traceability
        CREATE TABLE IF NOT EXISTS system_audit_log (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            learner_id TEXT,
            message TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """

        # Automated migration query to purge duplicate audit events if upgrading a legacy database
        migration_dedup_sql = """
        DELETE FROM system_audit_log
        WHERE log_id NOT IN (
            SELECT MAX(log_id)
            FROM system_audit_log
            GROUP BY event_type, learner_id
        );
        """

        schema_indexes_sql = """
        -- 4. B-Tree Indexes for rapid employer reporting & audit idempotency
        CREATE INDEX IF NOT EXISTS idx_learners_cohort ON learners (cohort_id);
        CREATE INDEX IF NOT EXISTS idx_learners_audit ON learners (is_audited);
        CREATE INDEX IF NOT EXISTS idx_cohorts_name ON cohorts (cohort_name);
        CREATE UNIQUE INDEX IF NOT EXISTS idx_audit_event_learner ON system_audit_log (event_type, learner_id);
        """

        conn = None
        try:
            conn = self.get_connection()
            with conn:
                conn.executescript(schema_tables_sql)
                conn.execute(migration_dedup_sql)
                conn.executescript(schema_indexes_sql)
            self.logger.info("Database schema initialized successfully at '%s'.", self.db_path)
        except sqlite3.Error as err:
            self.logger.critical("Fatal error initializing database schema: %s", err)
            raise
        finally:
            if conn:
                conn.close()

    def get_or_create_cohort(self, conn: sqlite3.Connection, cohort_name: str) -> int:
        """
        Query cohort_id by cohort_name; insert new cohort record if not already existing.
        Derives track name automatically (e.g. 'Data Science' from 'Data Science Cohort 5').

        Args:
            conn: Active database connection.
            cohort_name: Full cohort string.

        Returns:
            int: The primary key cohort_id.
        """
        cursor = conn.cursor()
        # Parameterized query to prevent SQL Injection
        cursor.execute("SELECT cohort_id FROM cohorts WHERE cohort_name = ?;", (cohort_name,))
        row = cursor.fetchone()
        if row:
            return int(row["cohort_id"])

        # Determine curriculum track from cohort name
        program_track = self._derive_program_track(cohort_name)

        # Parameterized insert
        cursor.execute(
            "INSERT INTO cohorts (cohort_name, program_track) VALUES (?, ?);",
            (cohort_name, program_track),
        )
        new_cohort_id = cursor.lastrowid
        self.logger.info(
            "Created new Cohort record: ID=%d, Name='%s', Track='%s'.",
            new_cohort_id,
            cohort_name,
            program_track,
        )
        return int(new_cohort_id)

    @staticmethod
    def _derive_program_track(cohort_name: str) -> str:
        """Helper to extract general discipline from cohort title."""
        name_lower = cohort_name.lower()
        if "data science" in name_lower:
            return "Data Science"
        elif "ai" in name_lower or "machine learning" in name_lower:
            return "AI & Machine Learning"
        elif "web" in name_lower or "full stack" in name_lower:
            return "Full Stack Web Development"
        elif "cloud" in name_lower:
            return "Cloud Computing"
        elif "cyber" in name_lower:
            return "Cybersecurity"
        else:
            return "General Tech"


# =====================================================================
# Core Data Ingestion & Transformation Pipeline
# =====================================================================

class IngestionPipeline:
    """
    Executes raw cohort CSV parsing, type casting, modulus quality audit
    sampling, polymorphic OOP instantiation, and transactional persistence.
    """

    def __init__(self, db_manager: DatabaseManager, logger: logging.Logger) -> None:
        """
        Initialize pipeline with database manager and logger.

        Args:
            db_manager: Instance of DatabaseManager.
            logger: Active logging instance.
        """
        self.db = db_manager
        self.logger = logger

    def parse_and_ingest(
        self,
        csv_file_path: str,
        simulate_load: bool = False,
        load_delay: float = 0.05,
    ) -> Dict[str, Any]:
        """
        Parse raw cohort CSV data and persist records into SQLite.
        Processes valid records while gracefully handling malformed CSV rows.

        Args:
            csv_file_path: Path to CSV data file.
            simulate_load: If True, adds artificial micro-delays for live process monitoring.
            load_delay: Delay in seconds per record when simulate_load is active.

        Returns:
            Dict[str, Any]: Execution summary telemetry metrics.
        """
        start_time = time.time()
        csv_path = os.path.abspath(csv_file_path)

        # Initialize summary metrics
        metrics = {
            "csv_file": csv_path,
            "total_rows_scanned": 0,
            "valid_records_ingested": 0,
            "invalid_rows_skipped": 0,
            "audit_flags_assigned": 0,
            "execution_duration_sec": 0.0,
            "transaction_status": "PENDING",
            "audited_learners": [],
        }

        self.logger.info("=" * 65)
        self.logger.info("Starting Ingestion Batch: '%s'", csv_path)
        self.logger.info("=" * 65)

        # 1. Validate File Existence and Non-Empty Status
        if not os.path.exists(csv_path):
            err_msg = f"Raw CSV source file not found at '{csv_path}'"
            self.logger.error("[FATAL FILE ERROR] %s", err_msg)
            metrics["transaction_status"] = "FAILED: FILE NOT FOUND"
            return metrics

        if os.path.getsize(csv_path) == 0:
            err_msg = f"Raw CSV source file at '{csv_path}' is empty (0 bytes)"
            self.logger.error("[FATAL FILE ERROR] %s", err_msg)
            metrics["transaction_status"] = "FAILED: EMPTY FILE"
            self._log_transaction_summary(metrics)
            return metrics

        # 2. Open Database Connection
        conn = None
        try:
            conn = self.db.get_connection()
        except sqlite3.Error as err:
            self.logger.critical("[DB ERROR] Unable to establish connection for ingestion: %s", err)
            metrics["transaction_status"] = "FAILED: DB CONNECTION REFUSED"
            return metrics

        # 3. Stream, Normalize & Parse CSV
        try:
            with open(csv_path, mode="r", encoding="utf-8-sig") as csv_handle:
                csv_raw_reader = csv.reader(csv_handle)

                # Extract and normalize headers
                try:
                    raw_headers = next(csv_raw_reader)
                except StopIteration:
                    self.logger.error("[EMPTY CSV ERROR] CSV file contains no rows.")
                    metrics["transaction_status"] = "FAILED: EMPTY FILE"
                    self._log_transaction_summary(metrics)
                    return metrics

                # Header Normalization: strip whitespace, lowercase, normalize delimiters
                normalized_headers = [
                    h.strip().lower().replace(" ", "_").replace("-", "_").strip('"\'')
                    for h in raw_headers if h is not None
                ]

                expected_headers = {"learner_id", "full_name", "cohort_name", "assessment_score", "enrollment_status"}
                if not expected_headers.issubset(set(normalized_headers)):
                    self.logger.error(
                        "[INVALID CSV FORMAT] Headers do not contain required fields: Expected %s, Found %s (Normalized: %s)",
                        expected_headers,
                        raw_headers,
                        normalized_headers,
                    )
                    metrics["transaction_status"] = "FAILED: MALFORMED HEADERS"
                    self._log_transaction_summary(metrics)
                    return metrics

                cursor = conn.cursor()

                for row_idx, row_values in enumerate(csv_raw_reader, start=1):
                    metrics["total_rows_scanned"] += 1

                    # Optional simulated load for Linux process monitoring
                    if simulate_load:
                        time.sleep(load_delay)

                    # Skip empty rows gracefully
                    if not row_values or all(not v.strip() for v in row_values):
                        metrics["invalid_rows_skipped"] += 1
                        self.logger.warning("[EMPTY ROW SKIPPED] Row #%d contains no values.", row_idx)
                        continue

                    # Strict Column Count Validation: intercept truncated or excess column rows
                    if len(row_values) != len(normalized_headers):
                        metrics["invalid_rows_skipped"] += 1
                        self.logger.warning(
                            "[MALFORMED ROW SKIPPED] Row #%d: Column count mismatch (expected %d columns, received %d) | Content: %s",
                            row_idx,
                            len(normalized_headers),
                            len(row_values),
                            row_values,
                        )
                        continue

                    # Construct dictionary using normalized headers
                    raw_row = dict(zip(normalized_headers, [v.strip() for v in row_values]))

                    # Robust record processing with exception intercept
                    is_valid, parsed_data, error_reason = self._sanitize_and_validate_row(raw_row, row_idx)

                    if not is_valid:
                        metrics["invalid_rows_skipped"] += 1
                        self.logger.warning(
                            "[MALFORMED ROW SKIPPED] Row #%d: %s | Raw Content: %s",
                            row_idx,
                            error_reason,
                            raw_row,
                        )
                        continue

                    # Unpack validated values
                    learner_id = parsed_data["learner_id"]
                    full_name = parsed_data["full_name"]
                    cohort_name = parsed_data["cohort_name"]
                    score_float = parsed_data["assessment_score"]
                    status = parsed_data["enrollment_status"]

                    # Modulus Operation: Flag every 10th valid learner for quality audit
                    # (Sprint 2 - Python Fundamentals requirement)
                    current_valid_count = metrics["valid_records_ingested"] + 1
                    is_audited = (current_valid_count % 10 == 0)

                    if is_audited:
                        metrics["audit_flags_assigned"] += 1
                        metrics["audited_learners"].append(learner_id)
                        self.logger.info(
                            "[QUALITY AUDIT TRIGGER] Valid record #%d: Learner %s (%s) flagged for QA sample (score=%.2f).",
                            current_valid_count,
                            learner_id,
                            full_name,
                            score_float,
                        )

                    # Instantiate polymorphic OOP Learner Model
                    # (Sprint 2 - OOP in Python requirement)
                    learner_entity = Learner(
                        learner_id=learner_id,
                        full_name=full_name,
                        cohort_name=cohort_name,
                        assessment_score=score_float,
                        enrollment_status=status,
                        is_audited=is_audited,
                    )

                    # Demonstrate Polymorphism via display_profile()
                    if is_audited or current_valid_count <= 2:
                        self.logger.debug("Polymorphic Profile Output:\n%s", learner_entity.display_profile())

                    # Resolve or insert Cohort foreign key
                    cohort_id = self.db.get_or_create_cohort(conn, cohort_name)

                    # Parameterized SQL execution strictly preventing SQL Injection
                    # Using ON CONFLICT(learner_id) DO UPDATE to preserve row identity during re-ingestion
                    cursor.execute(
                        """
                        INSERT INTO learners (
                            learner_id, full_name, cohort_id, assessment_score, enrollment_status, is_audited
                        ) VALUES (?, ?, ?, ?, ?, ?)
                        ON CONFLICT(learner_id) DO UPDATE SET
                            full_name = excluded.full_name,
                            cohort_id = excluded.cohort_id,
                            assessment_score = excluded.assessment_score,
                            enrollment_status = excluded.enrollment_status,
                            is_audited = excluded.is_audited;
                        """,
                        (
                            learner_entity.learner_id,
                            learner_entity.full_name,
                            cohort_id,
                            learner_entity.assessment_score,
                            learner_entity.enrollment_status,
                            1 if learner_entity.is_audited else 0,
                        ),
                    )

                    # Write system audit entry if flagged (Idempotent per learner and event_type)
                    if is_audited:
                        cursor.execute(
                            """
                            INSERT INTO system_audit_log (event_type, learner_id, message)
                            VALUES (?, ?, ?)
                            ON CONFLICT(event_type, learner_id) DO UPDATE SET
                                message = excluded.message,
                                timestamp = CURRENT_TIMESTAMP;
                            """,
                            (
                                "QUALITY_AUDIT_FLAG",
                                learner_entity.learner_id,
                                f"Flagged via modulus 10 operation at sequence #{current_valid_count}",
                            ),
                        )

                    metrics["valid_records_ingested"] += 1

                # Commit batch transaction
                conn.commit()
                metrics["transaction_status"] = "COMMITTED"
                self.logger.info("Database transaction committed successfully.")

        except (UnicodeDecodeError, UnicodeError) as enc_err:
            self.logger.error("[CSV ENCODING ERROR] Unable to decode CSV source with UTF-8: %s", enc_err)
            if conn:
                conn.rollback()
            metrics["transaction_status"] = "FAILED: CSV ENCODING ERROR"
        except (IOError, csv.Error) as file_err:
            self.logger.error("[FILE I/O ERROR] Unexpected error while streaming CSV: %s", file_err)
            if conn:
                conn.rollback()
            metrics["transaction_status"] = "ROLLED BACK: FILE I/O ERROR"
        except sqlite3.Error as db_err:
            self.logger.error("[DATABASE TRANSACTION ERROR] SQLite error encountered: %s", db_err)
            if conn:
                conn.rollback()
            metrics["transaction_status"] = "ROLLED BACK: DB ERROR"
        finally:
            if conn:
                conn.close()

        metrics["execution_duration_sec"] = round(time.time() - start_time, 4)

        # Log formal Transaction Summary to application_activity.log
        self._log_transaction_summary(metrics)

        return metrics

    def _sanitize_and_validate_row(
        self,
        raw_row: Dict[str, Any],
        row_idx: int,
    ) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Validate and scrub raw dictionary row. Ensures assessment scores
        are cast to float data type and bounds are satisfied.

        Args:
            raw_row: Dictionary produced by csv.DictReader.
            row_idx: CSV line index for diagnostic logging.

        Returns:
            Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
                (is_valid, parsed_dict, failure_reason)
        """
        try:
            # 1. Clean string keys and values with header normalization
            cleaned = {
                str(k).strip().lower().replace(" ", "_").replace("-", "_"): (str(v).strip() if v is not None else "")
                for k, v in raw_row.items() if k is not None
            }

            learner_id = cleaned.get("learner_id", "")
            full_name = cleaned.get("full_name", "")
            cohort_name = cleaned.get("cohort_name", "")
            score_str = cleaned.get("assessment_score", "")
            enrollment_status = cleaned.get("enrollment_status", "")

            # 2. Mandatory field check
            if not learner_id or not full_name or not cohort_name:
                return False, None, "Missing mandatory field (learner_id, full_name, or cohort_name)"

            # 3. Float casting with exception handling (Sprint 2 requirement)
            try:
                score_float = float(score_str)
            except (ValueError, TypeError):
                return False, None, f"Invalid assessment score value '{score_str}' (cannot cast to float)"

            # Check for non-finite values (NaN, +Infinity, -Infinity)
            # Comparisons with NaN (e.g., NaN < 0.0 or NaN > 100.0) evaluate to False,
            # which would silently bypass boundary checks and insert invalid/NULL states into SQLite.
            if not math.isfinite(score_float):
                return False, None, f"Assessment score must be a finite real number, received '{score_str}'"

            # 4. Assessment score boundary sanity check
            if score_float < 0.0 or score_float > 100.0:
                return False, None, f"Assessment score {score_float:.2f} outside valid [0, 100] range"

            # 5. Enrollment status validation (Strict: reject unknown statuses with descriptive error)
            valid_statuses = {"Active", "Graduated", "Dropped"}
            if enrollment_status not in valid_statuses:
                return (
                    False,
                    None,
                    f"Invalid enrollment_status '{enrollment_status}'. Permitted lifecycle statuses: {sorted(valid_statuses)}",
                )

            return True, {
                "learner_id": learner_id,
                "full_name": full_name,
                "cohort_name": cohort_name,
                "assessment_score": score_float,
                "enrollment_status": enrollment_status,
            }, None

        except Exception as unhandled_err:
            return False, None, f"Unexpected record parsing error: {unhandled_err}"

    def _log_transaction_summary(self, metrics: Dict[str, Any]) -> None:
        """Append formal transaction audit summary to application_activity.log."""
        summary_banner = (
            "\n"
            + "=" * 65 + "\n"
            + "     LEARMS DATA INGESTION TRANSACTION SUMMARY REPORT     \n"
            + "=" * 65 + "\n"
            + f" Execution Timestamp  : {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
            + f" Source File Path     : {metrics['csv_file']}\n"
            + f" Total Records Scanned: {metrics['total_rows_scanned']}\n"
            + f" Successfully Ingested: {metrics['valid_records_ingested']}\n"
            + f" Malformed Rows Skipt : {metrics['invalid_rows_skipped']}\n"
            + f" Modulus Audits Flagd : {metrics['audit_flags_assigned']}\n"
            + f" Audited Learner IDs  : {', '.join(metrics['audited_learners']) if metrics['audited_learners'] else 'None'}\n"
            + f" Transaction State    : {metrics['transaction_status']}\n"
            + f" Pipeline Duration    : {metrics['execution_duration_sec']:.4f} seconds\n"
            + "=" * 65 + "\n"
        )
        self.logger.info(summary_banner)


# =====================================================================
# Database Inspection & Audit Reporting Utility
# =====================================================================

def generate_database_report(db_path: str, logger: logging.Logger) -> None:
    """
    Query the SQLite database and display aggregated analytics, cohort counts,
    and the list of learners flagged for quality audit.

    Args:
        db_path: Path to sprints_learners.db.
        logger: Active logger.
    """
    if not os.path.exists(db_path):
        logger.error("Database file '%s' does not exist.", db_path)
        return

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        # 1. Total counts
        cursor.execute("SELECT COUNT(*) AS total FROM learners;")
        total_learners = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS total FROM cohorts;")
        total_cohorts = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS total FROM learners WHERE is_audited = 1;")
        total_audited = cursor.fetchone()["total"]

        cursor.execute("SELECT AVG(assessment_score) AS avg_score FROM learners;")
        avg_score = cursor.fetchone()["avg_score"] or 0.0

        print("\n" + "#" * 65)
        print("       SPRINTS LEARMS - DATABASE AUDIT & SUMMARY REPORT       ")
        print("#" * 65)
        print(f"Total Cohorts Tracked  : {total_cohorts}")
        print(f"Total Learners Stored  : {total_learners}")
        print(f"Average Learner Score  : {avg_score:.2f}%")
        print(f"Quality Audited Records: {total_audited} (Target: ~10% sample)")
        print("-" * 65)

        # 2. Cohort breakdown
        print("\n[ Cohort Enrollment & Performance Breakdown ]")
        cursor.execute("""
            SELECT 
                c.cohort_name, 
                c.program_track, 
                COUNT(l.learner_id) AS learner_count,
                ROUND(AVG(l.assessment_score), 2) AS avg_cohort_score
            FROM cohorts c
            LEFT JOIN learners l ON c.cohort_id = l.cohort_id
            GROUP BY c.cohort_id
            ORDER BY learner_count DESC;
        """)
        for row in cursor.fetchall():
            print(f"  * {row['cohort_name']:<42} | Track: {row['program_track']:<22} | Learners: {row['learner_count']:>2} | Avg: {row['avg_cohort_score']}%")

        # 3. Audited learners sample roster
        print("\n[ Flagged Quality Audit Sample Roster (10% Modulus Check) ]")
        cursor.execute("""
            SELECT l.learner_id, l.full_name, c.cohort_name, l.assessment_score, l.enrollment_status
            FROM learners l
            JOIN cohorts c ON l.cohort_id = c.cohort_id
            WHERE l.is_audited = 1
            ORDER BY l.learner_id;
        """)
        audited_rows = cursor.fetchall()
        for i, row in enumerate(audited_rows, start=1):
            print(f"  {i}. [{row['learner_id']}] {row['full_name']:<22} | Score: {row['assessment_score']:>6.2f}% | Cohort: {row['cohort_name']} | Status: {row['enrollment_status']}")

        print("#" * 65 + "\n")

    except sqlite3.Error as err:
        logger.error("Error generating database report: %s", err)
    finally:
        conn.close()


# =====================================================================
# CLI Entrypoint & Driver
# =====================================================================

def main() -> int:
    """
    Main execution entrypoint with command-line interface.

    Returns:
        int: Exit status code (0 for success, non-zero for error).
    """
    parser = argparse.ArgumentParser(
        description="Sprints LEARMS - Learner Assessment & Resource Management System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    default_csv = os.path.join(PROJECT_ROOT, "data", "raw_cohort_data.csv")
    default_db = os.path.join(PROJECT_ROOT, "data", "sprints_learners.db")
    default_log = os.path.join(PROJECT_ROOT, "logs", "application_activity.log")

    parser.add_argument("--csv", default=default_csv, help="Path to input raw CSV data file")
    parser.add_argument("--db", default=default_db, help="Path to target SQLite database")
    parser.add_argument("--log", default=default_log, help="Path to application activity log file")
    parser.add_argument("--simulate-load", action="store_true", help="Enable micro-delays for Linux process monitoring")
    parser.add_argument("--verify", action="store_true", help="Generate and print comprehensive database audit report")
    parser.add_argument("--test-edge-cases", action="store_true", help="Run ingestion on corrupted CSV to verify fault-tolerant row processing")

    args = parser.parse_args()

    # 1. Setup Logger
    logger = configure_logger(args.log)
    logger.info("Initializing Sprints LEARMS Core Engine v1.0.0")

    # 2. Initialize Database Manager & Tables
    db_mgr = DatabaseManager(args.db, logger)
    try:
        db_mgr.initialize_schema()
    except Exception as err:
        logger.critical("Fatal initialization fault: %s", err)
        return 1

    # 3. Ingestion Engine Execution
    pipeline = IngestionPipeline(db_mgr, logger)

    target_csv = args.csv
    if args.test_edge_cases:
        target_csv = os.path.join(PROJECT_ROOT, "data", "corrupted_sample_data.csv")
        logger.info("[EDGE CASE TESTING MODE ACTIVATED] Running against corrupted dataset: '%s'", target_csv)

    results = pipeline.parse_and_ingest(
        csv_file_path=target_csv,
        simulate_load=args.simulate_load,
    )

    # 4. Optional Database Verification & Report
    if args.verify or not args.test_edge_cases:
        generate_database_report(args.db, logger)

    return 0 if "COMMITTED" in results["transaction_status"] else 1


if __name__ == "__main__":
    sys.exit(main())
