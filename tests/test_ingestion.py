"""
Integration and Robustness Tests for LEARMS Ingestion Engine & SQLite Database.
Verifies schema constraints, modulus audit sampling, 100% ingestion uptime,
and SQL injection prevention.
"""

import os
import sqlite3
import tempfile
import unittest
import logging

from code.main import DatabaseManager, IngestionPipeline


class TestIngestionAndDatabase(unittest.TestCase):
    """Test suite for validating ingestion pipeline robustness and SQLite integrity."""

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
        # Create a CSV with 25 records
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

    def test_fault_tolerant_uptime_with_malformed_csv(self):
        """Verify 100% uptime: corrupted rows are skipped and valid rows are committed."""
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

        # Check that valid records were saved
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) AS total FROM learners;")
        self.assertEqual(cursor.fetchone()["total"], 2)
        conn.close()


if __name__ == "__main__":
    unittest.main()
