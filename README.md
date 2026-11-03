# Learner Assessment & Resource Management System (LEARMS)

[![Python Standard Library](https://img.shields.io/badge/Python-3.10%2B%20Core-3776AB?logo=python&logoColor=white)](#)
[![Database](https://img.shields.io/badge/Database-SQLite3%20Normalized-003B57?logo=sqlite&logoColor=white)](#)
[![OS Environment](https://img.shields.io/badge/Environment-Linux%20%7C%20WSL2%20Ubuntu-FCC624?logo=linux&logoColor=black)](#)
[![SCM](https://img.shields.io/badge/Version%20Control-Git%20Structured-F05032?logo=git&logoColor=white)](#)
[![Tests](https://img.shields.io/badge/Automated%20Tests-20%2F20%20Passing-10B981)](#)
[![Fault Tolerance](https://img.shields.io/badge/Ingestion%20Pipeline-Fault%20Tolerant-008DDA)](#)

> **Client:** Sprints (EdTech & Talent-Development Platform, MENA)  
> **Primary Stakeholder:** Fatima Rashid, Director of Technical Operations  
> **Lead Consultant:** Mohammed Wael, Junior Solutions Consultant  
> **Engagement:** Two-Week Capstone Engineering Engagement  
> **Release:** v1.0.0 Production Baseline  

---

## 1. Executive Summary & Business Challenge

**Sprints** bridges the gap between learning and employment across the MENA region by delivering market-driven tech bootcamps in **Data Science**, **AI & Machine Learning**, **Full Stack Web Development**, **Cloud Computing**, and **Cybersecurity**. 

### The Problem
As cohort volumes expanded, managing learner assessment data became an acute operational bottleneck. LMS tools exported raw data into fragmented flat text files. The systems administration team was forced to manually parse records, run disjointed ad-hoc scripts, and adjust folder permissions individually to provide reports for hiring partners. This decentralized process suffered from:
- **Data corruption & silent failures** due to unvalidated inputs.
- **Security vulnerabilities** from unstandardized directory permissions.
- **Lack of version control & auditability** across script iterations.

### The Solution: LEARMS
**LEARMS** is an automated, secure, Python-driven backend application paired with an ACID-compliant, Third Normal Form (3NF) SQLite database (`sprints_learners.db`). Engineered strictly using **core Python standard libraries** and native Linux CLI tools, LEARMS provides:
- **Fault-Tolerant Ingestion Pipeline:** Successfully processes valid records while isolating and logging malformed rows in tested edge-case scenarios.
- **Relational Normalization & SQL Injection Defense:** 100% Parameterized query execution (`?` placeholders).
- **Identity-Preserving Conflict Resolution:** Uses `ON CONFLICT(learner_id) DO UPDATE SET` to ensure idempotency and prevent record deletion side-effects during re-ingestion.
- **Automated Periodic Quality Audit Sampling:** Mathematically flags every 10th learner (`counter % 10 == 0`) for employer partner QA reviews.
- **Hardened Linux Security:** Primary administrative group configuration (`sprints_ops`, GID: 1003) and least-privilege permissions (`chmod 750`/`660`/`640`) enabling daily sysadmin operations without root privileges.

---

## 2. System Architecture & Flow

```text
       +--------------------------------------------------------+
       |            data/raw_cohort_data.csv                    |
       |  (learner_id, full_name, cohort_name, score, status)   |
       +--------------------------------------------------------+
                                   │
                                   ▼
       +--------------------------------------------------------+
       |           Header Normalization & Validation            |
       |    • Normalizes spacing, casing, and delimiters        |
       |    • Validates mandatory schema requirements           |
       +--------------------------------------------------------+
                                   │
                                   ▼
       +--------------------------------------------------------+
       |          Row Sanitization & Type Enforcement           |
       |    • Score cast strictly to float (try-except)         |
       |    • Status sanity check ('Active','Graduated',etc.)   |
       |    • Dead-letter logging on malformed rows             |
       +--------------------------------------------------------+
                                   │
                                   ▼
       +--------------------------------------------------------+
       |    Automated Periodic Quality Audit (% 10 Sampling)    |
       |    • Flags 10th, 20th, 30th, 40th valid record         |
       |    • Assigns is_audited = 1 & logs QA alert            |
       +--------------------------------------------------------+
                                   │
                                   ▼
       +--------------------------------------------------------+
       |               Polymorphic OOP Domain Models            |
       |    • Base User -> Specialized Learner Subclass         |
       |    • Dynamic dispatch: learner.display_profile()       |
       +--------------------------------------------------------+
                                   │
                                   ▼
       +--------------------------------------------------------+
       |       SQLite Relational Persistence Layer (3NF)        |
       |    • PRAGMA foreign_keys = ON;                         |
       |    • Parameterized SQL (? syntax) prevents SQLi        |
       |    • ON CONFLICT(learner_id) DO UPDATE (idempotent)    |
       |    • Atomic transaction commit with auto-rollback      |
       +--------------------------------------------------------+
             │                                            │
             ▼                                            ▼
+-------------------------+                 +---------------------------+
| data/sprints_learners.db|                 |logs/application_activity.log|
+-------------------------+                 +---------------------------+
```

---

## 3. Repository Directory Structure

```text
sprints_learms/
├── code/
│   ├── __init__.py                # Package exports
│   ├── models.py                  # Domain OOP models (User, Learner, Instructor)
│   └── main.py                    # Core ingestion pipeline, DB layer & CLI
├── data/
│   ├── raw_cohort_data.csv        # Production starter cohort data (45 learners)
│   ├── corrupted_sample_data.csv  # Edge-case test data (proves fault tolerance)
│   └── sprints_learners.db        # Normalized 3NF SQLite database
├── logs/
│   ├── linux_operations.log       # Terminal log of all Linux setup & monitoring commands
│   └── application_activity.log   # Application execution telemetry & transaction summaries
├── docs/
│   ├── PROJECT_CHARTER.md         # Discovery charter (milestone days 1-2)
│   ├── System_Architecture_Report.md # Markdown architectural documentation
│   ├── System_Architecture_Report.pdf# Publication-grade executive technical report
│   ├── Capstone_Presentation.md   # Presentation slide deck markdown source
│   └── Capstone_Presentation.pdf  # 10-slide executive presentation PDF
├── scripts/
│   ├── setup_linux_env.sh         # Linux provisioning & permission hardening
│   ├── monitor_process.sh         # Real-time process telemetry (ps/grep monitor)
│   ├── run_ingestion.sh           # Safe non-root execution wrapper
│   └── generate_documents.py      # Automated ReportLab PDF generator
├── tests/
│   ├── __init__.py
│   ├── test_models.py             # Unit tests for User, Learner, Instructor OOP
│   └── test_ingestion.py          # Integration tests (DB, CSV, Injection, Idempotency)
├── .gitignore                     # Git configuration ignoring temp & cache files
├── CHANGELOG.md                   # Chronological ledger of architectural decisions
├── DEMO_SCRIPT.md                 # 3-5 minute presentation walkthrough script
├── Demo_Walkthrough.mp4           # 4-minute 1080p demo walkthrough video
└── README.md                      # Comprehensive developer & operations guide
```

---

## 4. Quickstart Guide

### Prerequisites
- Python 3.10+ (Standard library only; **no third-party pip packages required** for runtime execution).
- SQLite 3.35+.
- Linux / WSL2 Ubuntu (for Linux permissions and process monitoring).
- Git.

### 1. Ingest Cohort Data & Verify Database
Run the core pipeline against the starter cohort data:
```bash
python code/main.py --verify
```
**Terminal Output:**
```text
[INFO] Initializing Sprints LEARMS Core Engine v1.0.0
[INFO] Database schema initialized successfully at 'data/sprints_learners.db'.
[INFO] Starting Ingestion Batch: 'data/raw_cohort_data.csv'
[INFO] [QUALITY AUDIT TRIGGER] Valid record #10: Learner SP-L-1010 flagged for QA sample.
[INFO] [QUALITY AUDIT TRIGGER] Valid record #20: Learner SP-L-1020 flagged for QA sample.
[INFO] [QUALITY AUDIT TRIGGER] Valid record #30: Learner SP-L-1030 flagged for QA sample.
[INFO] [QUALITY AUDIT TRIGGER] Valid record #40: Learner SP-L-1040 flagged for QA sample.
[INFO] Database transaction committed successfully.

=================================================================
     LEARMS DATA INGESTION TRANSACTION SUMMARY REPORT     
=================================================================
 Total Records Scanned: 45
 Successfully Ingested: 45
 Malformed Rows Skipt : 0
 Modulus Audits Flagd : 4 (10% Target Met)
 Transaction State    : COMMITTED
 Pipeline Duration    : 0.0081 seconds
=================================================================
```

### 2. Verify Ingestion Fault Tolerance on Corrupted Data
Demonstrate fault tolerance and zero-crash error handling against malformed float scores and missing values:
```bash
python code/main.py --test-edge-cases
```
The engine catches malformed rows (invalid string scores, negative grades, missing cohort titles), logs them to `logs/application_activity.log`, and commits all valid rows without crashing.

### 3. Run Automated Unit & Integration Tests
Execute the full test suite verifying OOP models, database integrity, idempotency, and SQL injection prevention:
```bash
python -m unittest discover -s tests -p "test_*.py" -v
```
**Execution Evidence (20/20 Passed):**
```text
test_csv_encoding_error (test_ingestion.TestIngestionAndDatabase) ... ok
test_database_functional_write_permission (test_ingestion.TestIngestionAndDatabase) ... ok
test_database_schema_and_foreign_keys (test_ingestion.TestIngestionAndDatabase) ... ok
test_duplicate_learner_id_on_conflict_update (test_ingestion.TestIngestionAndDatabase) ... ok
test_empty_csv_handling (test_ingestion.TestIngestionAndDatabase) ... ok
test_fault_tolerant_uptime_with_malformed_csv (test_ingestion.TestIngestionAndDatabase) ... ok
test_header_normalization (test_ingestion.TestIngestionAndDatabase) ... ok
test_header_only_csv_handling (test_ingestion.TestIngestionAndDatabase) ... ok
test_infinity_assessment_score_rejected (test_ingestion.TestIngestionAndDatabase) ... ok
test_logging_permission_failure (test_ingestion.TestIngestionAndDatabase) ... ok
test_missing_mandatory_headers (test_ingestion.TestIngestionAndDatabase) ... ok
test_modulus_audit_flagging (test_ingestion.TestIngestionAndDatabase) ... ok
test_nan_assessment_score_rejected (test_ingestion.TestIngestionAndDatabase) ... ok
test_repeated_ingestion_idempotency (test_ingestion.TestIngestionAndDatabase) ... ok
test_sql_injection_defense (test_ingestion.TestIngestionAndDatabase) ... ok
test_base_user_initialization_and_validation (test_models.TestDomainModels) ... ok
test_instructor_inheritance_and_polymorphism (test_models.TestDomainModels) ... ok
test_learner_inheritance_and_polymorphism (test_models.TestDomainModels) ... ok
test_score_grade_boundaries (test_models.TestDomainModels) ... ok
test_score_non_finite_and_out_of_bounds_validation (test_models.TestDomainModels) ... ok
----------------------------------------------------------------------
Ran 20 tests in 0.393s - OK
```

---

## 5. Linux Administration & Security (Sprint 3)

### Linux Environment Setup
Run the automated environment setup script inside WSL2 Ubuntu:
```bash
sudo ./scripts/setup_linux_env.sh
```
This script:
1. Installs `sqlite3` and `libsqlite3-dev` via `apt-get`.
2. Sets `sprints_ops` (GID: 1003) as the **Primary Group** for the operator (`usermod -g sprints_ops $USER`).
3. Hardens permissions:
   - `chmod 750 code/*.py scripts/*.sh`
   - `chmod 660 data/*.db data/*.csv` (Group read/write enabled for database updates)
   - `chmod 660 logs/*.log`
   - `chmod 640 docs/*.md *.md`
   - `chown -R $USER:sprints_ops .`
4. Validates write access as a non-root operator.

### Process Telemetry & Monitoring
Verify process memory and CPU consumption under load:
```bash
./scripts/monitor_process.sh
```
Output captures the active process using `ps aux | grep main.py`:
- **Executing User / Primary Group:** `USER: mw851 | GROUP: sprints_ops`
- **CPU Utilization:** 26.0% - 27.2%
- **Memory (RSS):** 20,344 KB (< 28 MB steady state)
- **Virtual Size (VSZ):** 26,356 KB

---

## 6. Rubric & Deliverables Compliance Matrix

| Sprint Scope | Requirement | Status | Evidence File |
| :--- | :--- | :---: | :--- |
| **Sprint 1 (SCM)** | Git repository & structured commit history | **MET (100%)** | `.git/`, Conventional Commits |
| **Sprint 1 (SWE)** | System architecture & schema documentation in Markdown & PDF | **MET (100%)** | `docs/System_Architecture_Report.pdf` |
| **Sprint 2 (OOP)** | Base `User` class; polymorphic `Learner` and `Instructor` subclasses | **MET (100%)** | `code/models.py` |
| **Sprint 2 (Fundamentals)**| Parse CSV, cast scores to float, % 10 periodic audit sampling | **MET (100%)** | `code/main.py` |
| **Sprint 2 (Database)** | Normalized 3NF SQLite database (`sprints_learners.db`), foreign keys | **MET (100%)** | `data/sprints_learners.db` |
| **Sprint 2 (Exceptions)** | Fault-tolerant pipeline, robust try-except around file I/O & SQL | **MET (100%)** | `code/main.py` |
| **Sprint 2 (Logging)** | Operational activity log & transaction summaries | **MET (100%)** | `logs/application_activity.log` |
| **Sprint 3 (Linux Basic)** | `apt-get install sqlite3` logged in terminal log | **MET (100%)** | `logs/linux_operations.log` |
| **Sprint 3 (Linux Advanced)**| Primary Group `sprints_ops`, permissions (`750`/`660`/`640`) | **MET (100%)** | `logs/linux_operations.log` |
| **Sprint 3 (Linux Advanced)**| `ps` & `grep` process monitoring of memory/CPU state | **MET (100%)** | `logs/linux_operations.log` |
| **Capstone Deliverable** | 8-10 slide final presentation deck (PDF & MD) | **MET (100%)** | `docs/Capstone_Presentation.pdf` |
| **Capstone Deliverable** | 3-5 minute recorded demo walkthrough (MP4) | **MET (100%)** | `Demo_Walkthrough.mp4` |

---

## 7. License & Credits
Developed by **Mohammed Wael** (Junior Solutions Consultant) for **Sprints EdTech**.  
All rights reserved © 2026 Sprints Technical Operations.
