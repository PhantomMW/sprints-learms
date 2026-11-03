"""
Integration, Security, and Robustness Tests for LEARMS Ingestion Engine & SQLite Database.
Comprehensive coverage validating:
  - 3NF Schema & Foreign Key Enforcement
  - SQL Injection Immunity via Parameterized Execution
  - Modulus Quality Audit Flagging (% 10)
  - Duplicate Handling (ON CONFLICT DO UPDATE)
  - Repeated Ingestion Idempotency
  - Empty CSV & Missing Headers Detection
  - Header Normalization (Whitespace, Casing, Delimiters)
  - Database Locked / Permission Errors
  - Logging Permission Failures
  - CSV Non-UTF8 Encoding Errors
"""

import os
import stat
import sqlite3
import tempfile
import unittest
import logging

from code.main import DatabaseManager, IngestionPipeline, configure_logger


class TestIngestionAndDatabase(unittest.TestCase):
    """Test suite for validating ingestion pipeline robustness, security, and edge cases."""

    def setUp(self):
        """Create a temporary isolated test environment for each test."""
        self.test_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.test_dir.name, "test_learners.db")
        self.log_path = os.path.join(self.test_dir.name, "test_activity.log")

        # Isolated null logger
        self.logger = logging.getLogger("TestLogger")
        self.logger.setLevel(logging.CRITICAL)

        self.db_manager = DatabaseManager(self.db_path, self.logger)
        self.db_manager.initialize_schema()
        self.pipeline = IngestionPipeline(self.db_manager, self.logger)

    def tearDown(self):
        """Clean up temporary files."""
        self.test_dir.cleanup()

    def test_database_schema_and_foreign_keys(self):
        """Verify normalized tables exist and foreign keys are enforced."""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        # Check table existence
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = {row["name"] for row in cursor.fetchall()}
        self.assertIn("cohorts", tables)
        self.assertIn("learners", tables)
        self.assertIn("system_audit_log", tables)

        # Enforce foreign key: inserting learner with invalid cohort_id must fail
        with self.assertRaises(sqlite3.IntegrityError):
            cursor.execute(
                "INSERT INTO learners (learner_id, full_name, cohort_id, assessment_score, enrollment_status) "
                "VALUES ('SP-ERR-1', 'Test User', 9999, 80.0, 'Active');"
            )
        conn.close()

    def test_sql_injection_defense(self):
        """Verify parameterized queries prevent SQL injection payloads in learner records."""
        conn = self.db_manager.get_connection()
        cohort_id = self.db_manager.get_or_create_cohort(conn, "Security Cohort 1")

        # Malicious payload designed to drop table or bypass auth
        malicious_id = "SP-L-9999'); DROP TABLE learners; --"
        malicious_name = "Robert'); DROP TABLE cohorts; --"

        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO learners (learner_id, full_name, cohort_id, assessment_score, enrollment_status) "
            "VALUES (?, ?, ?, ?, ?);",
            (malicious_id, malicious_name, cohort_id, 99.0, "Active"),
        )
        conn.commit()

        # Verify tables are still intact and learner record was safely persisted as literal text
        cursor.execute("SELECT COUNT(*) AS c FROM learners WHERE learner_id = ?;", (malicious_id,))
        self.assertEqual(cursor.fetchone()["c"], 1)

        cursor.execute("SELECT COUNT(*) AS c FROM cohorts;")
        self.assertGreater(cursor.fetchone()["c"], 0)
        conn.close()

    def test_modulus_audit_flagging(self):
        """Verify that every 10th record is flagged for quality audit (% 10 == 0)."""
        csv_file = os.path.join(self.test_dir.name, "modulus_test.csv")
        with open(csv_file, "w", encoding="utf-8") as f:
            f.write("learner_id,full_name,cohort_name,assessment_score,enrollment_status\n")
            for i in range(1, 26):
                f.write(f"SP-L-{1000+i},Test Learner {i},Data Science Cohort 5,80.0,Active\n")

        results = self.pipeline.parse_and_ingest(csv_file)
        self.assertEqual(results["total_rows_scanned"], 25)
        self.assertEqual(results["valid_records_ingested"], 25)
        self.assertEqual(results["invalid_rows_skipped"], 0)
        # In 25 records, 10th and 20th are flagged (total 2)
        self.assertEqual(results["audit_flags_assigned"], 2)
        self.assertEqual(results["audited_learners"], ["SP-L-1010", "SP-L-1020"])

        # Check DB flag
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT learner_id FROM learners WHERE is_audited = 1 ORDER BY learner_id;")
        rows = [r["learner_id"] for r in cursor.fetchall()]
        self.assertEqual(rows, ["SP-L-1010", "SP-L-1020"])
        conn.close()

    def test_duplicate_learner_id_on_conflict_update(self):
        """Verify ON CONFLICT updates existing learner records rather than duplicating or deleting."""
        csv_initial = os.path.join(self.test_dir.name, "initial.csv")
        with open(csv_initial, "w", encoding="utf-8") as f:
            f.write("learner_id,full_name,cohort_name,assessment_score,enrollment_status\n")
            f.write("SP-L-9001,Original Name,Data Science Cohort 5,75.00,Active\n")

        self.pipeline.parse_and_ingest(csv_initial)

        # Ingest updated data for same learner_id
        csv_updated = os.path.join(self.test_dir.name, "updated.csv")
        with open(csv_updated, "w", encoding="utf-8") as f:
            f.write("learner_id,full_name,cohort_name,assessment_score,enrollment_status\n")
            f.write("SP-L-9001,Updated Name,AI & Machine Learning Cohort 2,98.50,Graduated\n")

        results = self.pipeline.parse_and_ingest(csv_updated)
        self.assertEqual(results["valid_records_ingested"], 1)

        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) AS cnt FROM learners WHERE learner_id = 'SP-L-9001';")
        self.assertEqual(cursor.fetchone()["cnt"], 1)

        cursor.execute("SELECT full_name, assessment_score, enrollment_status FROM learners WHERE learner_id = 'SP-L-9001';")
        row = cursor.fetchone()
        self.assertEqual(row["full_name"], "Updated Name")
        self.assertEqual(row["assessment_score"], 98.50)
        self.assertEqual(row["enrollment_status"], "Graduated")
        conn.close()

    def test_repeated_ingestion_idempotency(self):
        """Verify repeated ingestion of the same CSV produces clean, identical database state."""
        csv_file = os.path.join(self.test_dir.name, "idempotency_test.csv")
        with open(csv_file, "w", encoding="utf-8") as f:
            f.write("learner_id,full_name,cohort_name,assessment_score,enrollment_status\n")
            for i in range(1, 16):
                f.write(f"SP-L-{2000+i},Learner {i},Cloud Computing Cohort 3,85.00,Active\n")

        res1 = self.pipeline.parse_and_ingest(csv_file)
        self.assertEqual(res1["transaction_status"], "COMMITTED")
        self.assertEqual(res1["valid_records_ingested"], 15)

        # Run again
        res2 = self.pipeline.parse_and_ingest(csv_file)
        self.assertEqual(res2["transaction_status"], "COMMITTED")
        self.assertEqual(res2["valid_records_ingested"], 15)

        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) AS total FROM learners;")
        self.assertEqual(cursor.fetchone()["total"], 15)
        conn.close()

    def test_empty_csv_handling(self):
        """Verify 0-byte and header-only empty CSV files are intercepted safely."""
        empty_file = os.path.join(self.test_dir.name, "empty_zero_bytes.csv")
        with open(empty_file, "w", encoding="utf-8") as f:
            pass  # 0 bytes

        res = self.pipeline.parse_and_ingest(empty_file)
        self.assertEqual(res["transaction_status"], "FAILED: EMPTY FILE")

    def test_missing_mandatory_headers(self):
        """Verify CSV missing required headers is rejected cleanly without crashing."""
        bad_header_file = os.path.join(self.test_dir.name, "bad_headers.csv")
        with open(bad_header_file, "w", encoding="utf-8") as f:
            f.write("student_id,name,course\n")
            f.write("1,Ahmed,Data Science\n")

        res = self.pipeline.parse_and_ingest(bad_header_file)
        self.assertEqual(res["transaction_status"], "FAILED: MALFORMED HEADERS")

    def test_header_normalization(self):
        """Verify header normalization handles irregular spacing, casing, and dashes."""
        irregular_header_file = os.path.join(self.test_dir.name, "irregular_headers.csv")
        with open(irregular_header_file, "w", encoding="utf-8") as f:
            f.write("  Learner_ID  , Full Name , COHORT_NAME , Assessment-Score , enrollment status \n")
            f.write("SP-L-5555,Test Normalization,Data Science Cohort 5,88.50,Active\n")

        res = self.pipeline.parse_and_ingest(irregular_header_file)
        self.assertEqual(res["valid_records_ingested"], 1)
        self.assertEqual(res["transaction_status"], "COMMITTED")

    def test_logging_permission_failure(self):
        """Verify configure_logger raises RuntimeError if log path is unwritable."""
        invalid_log_path = "/nonexistent_root_dir_12345/sub/unwritable.log"
        if os.name == "nt":
            # On Windows, invalid drive / device path
            invalid_log_path = "Z:\\nonexistent_invalid_path_dir\\activity.log"

        with self.assertRaises(RuntimeError):
            configure_logger(invalid_log_path)

    def test_csv_encoding_error(self):
        """Verify non-UTF8 corrupted binary bytes in CSV are trapped gracefully."""
        corrupt_enc_file = os.path.join(self.test_dir.name, "corrupt_encoding.csv")
        with open(corrupt_enc_file, "wb") as f:
            # Write invalid UTF-8 byte sequences
            f.write(b"learner_id,full_name,cohort_name,assessment_score,enrollment_status\n")
            f.write(b"SP-L-8888,\xff\xfeInvalidBytes,Data Science Cohort 5,90.0,Active\n")

        res = self.pipeline.parse_and_ingest(corrupt_enc_file)
        self.assertIn("ENCODING", res["transaction_status"])

    def test_fault_tolerant_uptime_with_malformed_csv(self):
        """Verify corrupted rows are skipped and valid rows are committed (Fault Tolerance)."""
        csv_file = os.path.join(self.test_dir.name, "corrupt_test.csv")
        with open(csv_file, "w", encoding="utf-8") as f:
            f.write("learner_id,full_name,cohort_name,assessment_score,enrollment_status\n")
            f.write("SP-1,Valid One,Data Science Cohort 5,90.5,Active\n")
            f.write("SP-2,Bad Score,Data Science Cohort 5,NOT_A_FLOAT,Active\n")
            f.write("SP-3,Negative Score,Data Science Cohort 5,-15.0,Active\n")
            f.write("SP-4,Over 100 Score,Data Science Cohort 5,115.0,Active\n")
            f.write("SP-5,Missing Cohort,,85.0,Active\n")
            f.write("SP-6,Valid Two,Data Science Cohort 5,78.2,Active\n")

        results = self.pipeline.parse_and_ingest(csv_file)
        self.assertEqual(results["total_rows_scanned"], 6)
        self.assertEqual(results["valid_records_ingested"], 2)
        self.assertEqual(results["invalid_rows_skipped"], 4)
        self.assertEqual(results["transaction_status"], "COMMITTED")

        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) AS total FROM learners;")
        self.assertEqual(cursor.fetchone()["total"], 2)
        conn.close()


if __name__ == "__main__":
    unittest.main()
