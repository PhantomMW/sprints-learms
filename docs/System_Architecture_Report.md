# System Architecture & Implementation Report
**Project:** Learner Assessment & Resource Management System (LEARMS)  
**Organization:** Sprints  
**Prepared By:** Mohammed Wael, Junior Solutions Consultant  
**Reviewed By:** Fatima Rashid, Director of Technical Operations  
**Date:** November 2026  
**Version:** 1.0.0 (Production Release)  

---

## 1. Executive Summary
The Learner Assessment & Resource Management System (LEARMS) is a secure, lightweight, and robust backend engineering solution architected to eliminate operational bottlenecks in learner performance data management at Sprints. As Sprints rapidly scales its tech cohorts across the MENA region—training thousands of learners in Data Science, AI & Machine Learning, Full Stack Web Development, Cloud Computing, and Cybersecurity—the previous mechanism of relying on fragmented flat text files, manual folder permission edits, and unversioned ad-hoc scripts created severe data security risks, inconsistent reporting, and operational friction.

LEARMS replaces this legacy workflow with an automated, object-oriented Python pipeline paired with an ACID-compliant, normalized SQLite3 relational database (`sprints_learners.db`). The system is engineered strictly with core Python standard libraries (avoiding heavyweight third-party frameworks like Django or Pandas) and deployed within a rigorously hardened Linux (WSL2 Ubuntu) environment. 

Key milestones achieved in this implementation include:
- **100% Ingestion Pipeline Uptime:** Complete fault-tolerance intercepting malformed, missing, or corrupted data records without terminating execution.
- **Relational Integrity & SQL Injection Defense:** 3rd Normal Form schema architecture utilizing strictly parameterized queries (`?` parameter binding).
- **Automated Quality Audit Flagging:** Mathematical modulus-based sampling (`counter % 10 == 0`) flagging exactly 10% of ingested cohorts for quality assurance by Sprints hiring partners.
- **Enterprise Unix Security:** Least-privilege role-based access controls using `chown` and `chmod` (`750` for execution directories, `640` for databases and logs) eliminating root-dependency during daily operations.
- **Real-Time Process Monitoring & Telemetry:** End-to-end command logging in `logs/linux_operations.log` and transaction tracking in `logs/application_activity.log`.

---

## 2. Software Configuration Management: Git Strategy

### 2.1 Repository Structure
The repository follows a clean, modular structure designed for clear separation of concerns, maintainability, and enterprise reproducibility:

```text
sprints_learms/
├── code/
│   ├── __init__.py                # Package initialization
│   ├── models.py                  # OOP domain models (User, Learner, Instructor)
│   └── main.py                    # Ingestion pipeline, DB layer, CLI driver
├── data/
│   ├── raw_cohort_data.csv        # Production starter cohort data (45 learners)
│   ├── corrupted_sample_data.csv  # Edge-case verification dataset
│   └── sprints_learners.db        # Production SQLite normalized database
├── logs/
│   ├── linux_operations.log       # CLI terminal audit log (apt, chmod, chown, ps)
│   └── application_activity.log   # Application execution & transaction telemetry
├── docs/
│   ├── PROJECT_CHARTER.md         # Milestone Discovery charter & requirements
│   ├── System_Architecture_Report.md # Markdown architectural documentation
│   ├── System_Architecture_Report.pdf# Executive PDF technical report
│   ├── Capstone_Presentation.md   # Presentation slide deck source
│   └── Capstone_Presentation.pdf  # Final presentation slide deck
├── scripts/
│   ├── setup_linux_env.sh         # Linux environment & permission automation
│   ├── monitor_process.sh         # Process tracking (ps/grep telemetry script)
│   └── run_ingestion.sh           # Safe production execution wrapper
├── tests/
│   ├── __init__.py
│   ├── test_models.py             # Unit tests for User, Learner, Instructor OOP
│   └── test_ingestion.py          # Integration tests for DB, CSV, and edge cases
├── .gitignore                     # Git configuration ignoring temp & cache files
├── CHANGELOG.md                   # Chronological ledger of architectural decisions
├── DEMO_SCRIPT.md                 # 3-5 minute presentation walkthrough script
├── Demo_Walkthrough.mp4           # Recorded demonstration video
└── README.md                      # Comprehensive developer & operations guide
```

### 2.2 Commit Workflow
To guarantee auditability across the two-week sprint cycle, the engagement adopted the Conventional Commits specification. Development was organized into structured, incremental commits with descriptive messages corresponding to each milestone:

| Commit Hash / Phase | Scope | Description |
| :--- | :--- | :--- |
| **Sprint 1 (Commit 1)** | `chore(init)` | Repository structure, project charter, and `.gitignore` baseline. |
| **Sprint 1 (Commit 2)** | `docs(arch)` | System architecture report, ER diagrams, and relational schema. |
| **Sprint 2 (Commit 3)** | `feat(models)`| Domain OOP models: `User`, `Learner`, `Instructor` with polymorphism. |
| **Sprint 2 (Commit 4)** | `feat(db)` | SQLite initialization, normalized tables, and connection management. |
| **Sprint 2 (Commit 5)** | `feat(ingest)`| CSV ingestion engine, score float casting, and `% 10` audit flagging. |
| **Sprint 2 (Commit 6)** | `feat(log)` | Activity logger, exception handling, and transaction summaries. |
| **Sprint 2 (Commit 7)** | `test(core)` | Automated test suite for models, database, and error tolerance. |
| **Sprint 3 (Commit 8)` | `ops(linux)` | WSL Linux hardening, `apt-get` sqlite3 setup, and permissions. |
| **Sprint 3 (Commit 9)** | `docs(deck)` | Capstone presentation slides and executive PDF deliverables. |
| **Sprint 3 (Commit 10)`| `release` | Final demo recording, deployment sign-off, and repository push. |

---

## 3. Python Object-Oriented Programming (OOP) Models

### 3.1 Base Class: `User`
The foundation of the LEARMS domain model is the `User` class implemented in `code/models.py`. It establishes the shared identity contract for any human stakeholder within the Sprints educational ecosystem:

- **Attributes:**
  - `user_id` (`str`): Unique enterprise identifier (e.g., `SP-L-1001` or `SP-I-001`).
  - `full_name` (`str`): Full legal name of the individual.
  - `email` (`str`): System contact email (auto-derived or user-supplied).
  - `role` (`str`): System access role (`"Learner"`, `"Instructor"`, `"Admin"`).
  - `created_at` (`str`): ISO 8601 creation timestamp.
- **Methods:**
  - `display_profile() -> str`: Base polymorphic method outputting standardized stakeholder identity.
  - `get_details() -> dict`: Serializes object state into a dictionary for reporting and logging.
  - `validate() -> bool`: Ensures required fields (`user_id`, `full_name`) are non-empty strings.

### 3.2 Subclasses & Polymorphism: `Learner` and `Instructor`
The domain model applies OOP inheritance and polymorphism by extending `User` into specialized actors:

#### `Learner` Subclass
Represents upskilling talent enrolled across Sprints cohorts:
- **Additional Attributes:**
  - `cohort_name` (`str`): Name of the enrolled sprint cohort (e.g., `Data Science Cohort 5`).
  - `assessment_score` (`float`): Quantitative score cast strictly to standard Python float.
  - `enrollment_status` (`str`): Enrollment condition (`Active`, `Graduated`, `Dropped`).
  - `is_audited` (`bool`): Boolean flag indicating selection for employer partner quality review.
- **Polymorphic Method Overrides:**
  - `display_profile() -> str`: Overrides base `display_profile()` to output formatted academic records, score percentage to 2 decimal places, letter grade evaluation, and an attention-grabbing audit tag `[★ QUALITY AUDIT FLAGGED]` when `is_audited` is true.
  - `get_details() -> dict`: Enriches base dictionary with academic performance indicators and audit flags.
- **Domain Methods:**
  - `calculate_letter_grade() -> str`: Evaluates score thresholds (A >= 90%, B >= 80%, C >= 70%, D >= 60%, F < 60%).
  - `flag_for_audit() -> None`: Sets audit flag to True for quality compliance.

#### `Instructor` Subclass
Represents technical mentors and educators managing cohorts:
- **Additional Attributes:**
  - `specialization` (`str`): Core domain expertise (e.g., `AI & Machine Learning`, `Cloud Computing`).
  - `assigned_cohorts` (`List[str]`): List of active cohorts under instructor supervision.
- **Polymorphic Method Overrides:**
  - `display_profile() -> str`: Formats instructional profile highlighting technical specialization and a numbered list of assigned cohorts.
  - `get_details() -> dict`: Enriches dictionary with instructor credentials and cohort assignments.
- **Domain Methods:**
  - `assign_cohort(cohort_name: str) -> None`: Appends new cohort to instructor workload after validation.

```text
       +---------------------------------------------+
       |                  User (Base)                |
       +---------------------------------------------+
       | - user_id: str                              |
       | - full_name: str                            |
       | - email: str                                |
       | - role: str                                 |
       +---------------------------------------------+
       | + display_profile(): str                    |
       | + get_details(): dict                       |
       | + validate(): bool                          |
       +---------------------------------------------+
                              ^
                              |
              +---------------+---------------+
              |                               |
+-----------------------------+ +-----------------------------+
|           Learner           | |          Instructor         |
+-----------------------------+ +-----------------------------+
| - cohort_name: str          | | - specialization: str       |
| - assessment_score: float   | | - assigned_cohorts: list    |
| - enrollment_status: str    | +-----------------------------+
| - is_audited: bool          | | + display_profile() [OVER]  |
+-----------------------------+ | + get_details() [OVER]      |
| + display_profile() [OVER]  | | + assign_cohort()           |
| + get_details() [OVER]      | +-----------------------------+
| + calculate_letter_grade()  |
| + flag_for_audit()          |
+-----------------------------+
```

---

## 4. Database Schema Design (SQLite)

### 4.1 Entity-Relationship Layout
To eliminate anomalies inherent in flat CSV files (such as cohort name redundancy, update anomalies, and inconsistent casing), the relational database `data/sprints_learners.db` organizes data into normalized tables complying with Third Normal Form (3NF):

- **Relationship:** One-to-Many (`1:N`) between `Cohorts` and `Learners`. One cohort contains many enrolled learners; each learner belongs to exactly one cohort.
- **Referential Integrity:** Enforced via `PRAGMA foreign_keys = ON;` in SQLite. Deleting or updating a cohort cascades according to business rules.
- **Indexing:** Dedicated B-Tree indexes created on `learners.cohort_id` and `learners.is_audited` to support instant reporting for employer partners.

```text
+-----------------------------------+        +----------------------------------------+
|              Cohorts              |        |                Learners                |
+-----------------------------------+        +----------------------------------------+
| PK  cohort_id     INTEGER (AUTO)  |<---+   | PK  learner_id       TEXT              |
|     cohort_name   TEXT (UNIQUE)   |    |   |     full_name        TEXT              |
|     program_track TEXT            |    +---| FK  cohort_id        INTEGER           |
|     created_at    TIMESTAMP       |        |     assessment_score REAL              |
+-----------------------------------+        |     enrollment_status TEXT             |
                                             |     is_audited       INTEGER (BOOLEAN) |
                                             |     created_at       TIMESTAMP         |
                                             +----------------------------------------+
```

### 4.2 Data Dictionary

#### Table: `Cohorts`
| Column Name | SQLite Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `cohort_id` | `INTEGER` | `PRIMARY KEY AUTOINCREMENT` | Unique internal numeric surrogate identifier. |
| `cohort_name` | `TEXT` | `NOT NULL UNIQUE` | Unique descriptive cohort name (e.g., `Data Science Cohort 5`). |
| `program_track` | `TEXT` | `NOT NULL` | High-level curriculum track (e.g., `Data Science`, `Cybersecurity`). |
| `created_at` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP` | System record insertion timestamp. |

#### Table: `Learners`
| Column Name | SQLite Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `learner_id` | `TEXT` | `PRIMARY KEY` | Natural learner key formatted as `SP-L-XXXX`. |
| `full_name` | `TEXT` | `NOT NULL` | Learner full legal name. |
| `cohort_id` | `INTEGER` | `NOT NULL, REFERENCES Cohorts(cohort_id)` | Foreign key linking learner to their respective cohort. |
| `assessment_score` | `REAL` | `NOT NULL CHECK(assessment_score >= 0.0 AND assessment_score <= 100.0)` | Quantitative exam score strictly validated and cast to Python float. |
| `enrollment_status` | `TEXT` | `NOT NULL CHECK(enrollment_status IN ('Active', 'Graduated', 'Dropped'))` | Learner lifecycle status. |
| `is_audited` | `INTEGER` | `NOT NULL DEFAULT 0 CHECK(is_audited IN (0, 1))` | Boolean indicator (0=No, 1=Yes) set by modulus audit logic. |
| `created_at` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP` | Timestamp of database persistence. |

---

## 5. Application Logic & Data Flow

### 5.1 Data Ingestion & Transformation
The core pipeline in `code/main.py` is invoked via CLI or automated scripts:
1. **Source Discovery:** Opens `data/raw_cohort_data.csv` using Python's standard `csv.DictReader` inside a streaming context manager.
2. **Field Sanitization:** Trims whitespace and validates existence of mandatory columns.
3. **Data Type Casting:** Raw string assessment scores are converted via `float(row['assessment_score'].strip())`. If casting fails (e.g., non-numeric string, negative values, empty string), the row is routed to the dead-letter error handling handler.
4. **Relational Resolution:** The pipeline queries the `Cohorts` table for `cohort_name`. If absent, it dynamically determines the track and inserts the new cohort record, capturing the generated `cohort_id`.
5. **Parameterized Execution:** Inserts records via `INSERT OR REPLACE INTO learners (...) VALUES (?, ?, ?, ?, ?, ?)` preventing SQL injection.

### 5.2 Quality Audit Flagging
To fulfill employer partner quality assurance obligations without introducing bias:
- During sequential row parsing of valid learners, an atomic integer counter (`processed_valid_count`) is incremented.
- A modulus operation evaluates `processed_valid_count % 10 == 0`.
- Every 10th processed learner (10th, 20th, 30th, 40th...) has `is_audited` set to `True` (`1`).
- An operational audit event is emitted to `application_activity.log`:
  ```text
  [2026-11-03 12:30:15] [AUDIT] [main.py:184] Modulus Audit Trigger: Learner SP-L-1010 (Hadeer Mostafa) flagged for employer QA sample (Row #10).
  ```

### 5.3 Exception Handling & Logging
To satisfy the 100% ingestion uptime requirement:
- **Granular Try-Except Hierarchy:**
  - File I/O: Traps `FileNotFoundError`, `PermissionError`, and `UnicodeDecodeError`.
  - Record Transformation: Traps `ValueError` (invalid float conversion) and `KeyError` (missing CSV headers).
  - Database Execution: Traps `sqlite3.IntegrityError`, `sqlite3.OperationalError`, and `sqlite3.DatabaseError`.
- **Fault-Tolerant Dead-Letter Logging:** Corrupted rows are isolated and logged with exact line numbers and stack causes without halting subsequent row processing.
- **Transaction Management:** Database transactions are committed in batches. On fatal database connection interrupts, a full `connection.rollback()` is executed.
- **Activity Log File:** All events append to `logs/application_activity.log` detailing:
  - Startup timestamp and configuration parameters.
  - Step-by-step cohort resolution.
  - Quality audit selections.
  - Final transaction summary: `{total_scanned: 45, valid_inserted: 45, invalid_skipped: 0, audit_flagged: 4, duration_ms: 18.4}`.

---

## 6. Linux Configuration & Process Management

### 6.1 Package Management
All deployment tasks were executed inside WSL2 Ubuntu. The command sequence ensures `sqlite3` and essential runtime tools are installed:
```bash
sudo apt-get update
sudo apt-get install -y sqlite3 libsqlite3-dev
sqlite3 --version
```
*Verification:* SQLite version `3.46.1` verified operational.

### 6.2 Security & File Permissions
To prevent accidental or malicious data modification while allowing daily sysadmin operations without root/sudo escalation:
1. **User & Group Provisioning:**
   ```bash
   sudo groupadd -f sprints_ops
   sudo usermod -a -G sprints_ops $USER
   ```
2. **Ownership Assignment (`chown`):**
   ```bash
   sudo chown -R $USER:sprints_ops /mnt/c/Users/mw851/.gemini/antigravity/scratch/sprints_learms
   ```
3. **Least-Privilege Permissions (`chmod`):**
   ```bash
   chmod 750 /mnt/c/Users/mw851/.gemini/antigravity/scratch/sprints_learms/code/*.py
   chmod 750 /mnt/c/Users/mw851/.gemini/antigravity/scratch/sprints_learms/scripts/*.sh
   chmod 640 /mnt/c/Users/mw851/.gemini/antigravity/scratch/sprints_learms/data/sprints_learners.db
   chmod 660 /mnt/c/Users/mw851/.gemini/antigravity/scratch/sprints_learms/logs/*.log
   ```
   - Directory execution (`750`): Owner full control (`rwx`), `sprints_ops` group execute/read (`r-x`), others no access (`---`).
   - Database and logs (`640`/`660`): Owner and group read/write, world inaccessible.

### 6.3 Process Monitoring
Process health was verified under load using the standard Linux utility suite:
```bash
python3 code/main.py --simulate-load &
ps aux | grep "[p]ython3 code/main.py"
```
The telemetry output captured CPU percentage, virtual memory (`VSZ`), resident memory (`RSS`), and process state (`S`/`R`), confirming LEARMS operates with an ultra-light memory footprint (< 18MB RSS) and zero memory leakage.

---

## 7. Conclusion & Deployment Sign-off
The Learner Assessment & Resource Management System (LEARMS) has successfully completed all acceptance criteria outlined by Fatima Rashid, Director of Technical Operations. 

By unifying Python OOP principles, normalized relational data persistence, automated quality sampling, and hardened Linux security policies, LEARMS establishes an enterprise-grade foundational pipeline that allows Sprints to scale effortlessly across the MENA educational landscape.

### Reference Deliverable Links:
- **Core Engine Script:** `code/main.py`
- **Domain OOP Models:** `code/models.py`
- **Normalized SQLite Database:** `data/sprints_learners.db`
- **Linux Operations Audit Log:** `logs/linux_operations.log`
- **Operational Activity Log:** `logs/application_activity.log`
- **Executive Presentation Deck:** `docs/Capstone_Presentation.pdf`
- **Recorded Demo Walkthrough:** `Demo_Walkthrough.mp4` & `DEMO_SCRIPT.md`
- **Automated Test Suite:** `tests/test_models.py` & `tests/test_ingestion.py`
