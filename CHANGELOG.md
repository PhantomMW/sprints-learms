# Sprints LEARMS — Engineering Changelog & Architectural Decisions

All notable technical and architectural decisions for the **Learner Assessment & Resource Management System (LEARMS)** are documented in this ledger, organized chronologically by capstone sprint milestones.

---

## [1.0.1] - 2026-11-03 (Quality Hardening & Technical Audit Release)

### Ingestion Engine & Mathematical Rigor
- **Added:** Mathematical validation using `math.isfinite()` in `code/main.py` and `code/models.py` to intercept `NaN`, `+Infinity`, and `-Infinity` float values, preventing silent bypass of numerical bounds and constraint corruption in SQLite.
- **Changed:** Transitioned SQLite ingestion policy from destructive `INSERT OR REPLACE` to deterministic `INSERT INTO learners (...) ON CONFLICT(learner_id) DO UPDATE SET`, preserving primary key row identity and preventing foreign key cascading side-effects during re-ingestion.
- **Added:** Robust CSV header normalization routine stripping whitespace, lowercasing, and mapping hyphens to underscores before `csv.reader` dictionary mapping.
- **Added:** Graceful processing of header-only CSV files (0 data rows) resulting in clean status `COMMITTED` without unhandled exceptions.
- **Changed:** Refactored `configure_logger()` to enforce mandatory external activity logging: failure to create or append to `application_activity.log` now raises a fatal `RuntimeError` rather than silently continuing console-only.

### Linux Systems Administration & Security Hardening
- **Changed:** Hardened permission matrix in `scripts/setup_linux_env.sh` to `chmod 660` for database files (`data/*.db`) and directory, enabling group write transactions for non-root operators.
- **Changed:** Configured `sprints_ops` as the **Primary Group** (`usermod -g sprints_ops mw851`, `gid=1003`) rather than a secondary group, verified via `id mw851`.
- **Added:** Functional SQLite write permission test in `scripts/setup_linux_env.sh` executing a temporary table creation, row insertion, and table drop transaction as the non-root operator.
- **Changed:** Fixed `scripts/monitor_process.sh` to remove error suppression (`|| true`), capturing and verifying the exact application exit status (`$?`).
- **Changed:** Corrected Linux distribution version in `logs/linux_operations.log` to `Ubuntu 26.04.1 LTS (Resolute Raccoon)` matching the host WSL2 environment.

### Verification & Documentation Deliverables
- **Added:** Expanded automated test suite in `tests/test_ingestion.py` and `tests/test_models.py` to 20 comprehensive unit tests covering NaN rejection, Infinity handling, non-finite bounds, header-only CSVs, duplicate updates, and functional SQLite write transactions (20/20 passed in < 0.40s).
- **Added:** Comprehensive Demo Video Narration Script `docs/DEMO_SCRIPT.md` detailing all 8 video scenes.
- **Updated:** Updated `docs/PROJECT_CHARTER.md`, `README.md`, `docs/System_Architecture_Report.pdf`, and `docs/Capstone_Presentation.pdf`.

---

## [1.0.0] - 2026-11-03 (Sprint 3 Release & Deployment Sign-off)

### Sprint 3 - Linux Operations & Systems Administration
- **Added:** Automated Linux provisioning script `scripts/setup_linux_env.sh` executing `apt-get update` and installing `sqlite3` and `libsqlite3-dev` on WSL2 Ubuntu.
- **Added:** Non-root role-based security model provisioning the `sprints_ops` administrative group.
- **Changed:** Configured least-privilege directory permissions:
  - `chmod 750` for Python source files and Bash scripts (owner full, group read/execute, world blocked).
  - `chmod 640` for relational database (`data/sprints_learners.db`).
  - `chmod 660` for operational logs (`logs/application_activity.log`).
- **Added:** Telemetry monitoring utility `scripts/monitor_process.sh` tracking active PID, `%CPU` (21-23%), `%MEM` (0.5%), and Resident Set Size (`RSS < 28 MB`) via `ps aux | grep main.py`.
- **Added:** Terminal operations audit log `logs/linux_operations.log` providing 100% third-party reproducibility.
- **Added:** Executive Capstone Presentation deck `docs/Capstone_Presentation.pdf` (10 landscape slides).
- **Added:** 4-minute 1080p demo walkthrough video `Demo_Walkthrough.mp4` and comprehensive script `DEMO_SCRIPT.md`.

---

## [0.2.0] - 2026-11-02 (Sprint 2 - OOP, Database & Ingestion Engine)

### Sprint 2 - Object-Oriented Domain Models
- **Added:** Base class `User` in `code/models.py` encapsulating stakeholder identity, validation, and serialization.
- **Added:** Subclass `Learner(User)` overriding `display_profile()` and `get_details()` to demonstrate polymorphism, score float formatting, letter grade derivation, and quality audit badges (`[★ QUALITY AUDIT FLAGGED]`).
- **Added:** Subclass `Instructor(User)` overriding `display_profile()` to showcase mentor credentials and assigned cohort tracks.

### Sprint 2 - SQLite Relational Persistence
- **Added:** Third Normal Form (3NF) relational database `data/sprints_learners.db` with normalized tables:
  - `cohorts`: `cohort_id` (PK), `cohort_name` (UNIQUE), `program_track`, `created_at`.
  - `learners`: `learner_id` (PK), `full_name`, `cohort_id` (FK -> cohorts), `assessment_score` (REAL), `enrollment_status`, `is_audited` (BOOLEAN).
  - `system_audit_log`: Historical event traceability.
- **Enforced:** `PRAGMA foreign_keys = ON;` upon connection open.
- **Enforced:** Strict parameterized SQL queries (`?` parameter binding) to eliminate SQL injection vulnerabilities.

### Sprint 2 - Ingestion Engine & Quality Auditing
- **Added:** Core pipeline `code/main.py` streaming `data/raw_cohort_data.csv` via `csv.DictReader`.
- **Added:** Strict type casting converting string assessment scores to Python `float`.
- **Added:** Mathematical modulus operation (`processed_valid_counter % 10 == 0`) flagging exactly 10% of ingested learners for employer QA review (flagged SP-L-1010, SP-L-1020, SP-L-1030, SP-L-1040).
- **Added:** Granular `try-except` hierarchy ensuring 100% ingestion uptime: invalid scores and malformed rows are logged to `logs/application_activity.log` without halting pipeline execution.
- **Added:** Comprehensive automated test suite in `tests/test_models.py` and `tests/test_ingestion.py` covering models, schema constraints, SQL injection defense, and fault tolerance (8/8 tests passed).

---

## [0.1.0] - 2026-10-31 (Sprint 1 - Software Configuration Management & Engineering)

### Sprint 1 - Software Configuration Management
- **Added:** Local Git repository initialized with structured commit convention (`chore:`, `docs:`, `feat:`, `ops:`, `release:`).
- **Added:** Enterprise `.gitignore` suppressing cache, build, temporary, and virtual environment artifacts.
- **Added:** Project Charter `docs/PROJECT_CHARTER.md` defining scope, risks, assumptions, and stakeholder alignment.
- **Added:** Comprehensive technical architecture specification `docs/System_Architecture_Report.md` and compiled publication-grade PDF `docs/System_Architecture_Report.pdf`.
