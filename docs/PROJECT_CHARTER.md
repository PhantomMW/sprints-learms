# Project Charter: Learner Assessment & Resource Management System (LEARMS)

**Project Name:** Learner Assessment & Resource Management System (LEARMS)  
**Client Organization:** Sprints (EdTech & Talent-Development Platform)  
**Primary Stakeholder:** Fatima Rashid, Director of Technical Operations  
**Lead Consultant / Engineer:** Mohammed Wael, Junior Solutions Consultant  
**Engagement Duration:** 2 Weeks (Capstone Acceleration)  
**Date:** November 2026  
**Status:** Approved & Baselined  

---

## 1. Problem Statement & Background
Sprints bridges the gap between learning and employment across the MENA region by offering market-driven tech cohorts (Data Science, AI & ML, Web Development, Cloud Computing, and Cybersecurity). As cohort sizes scale exponentially, managing learner assessment data has become a critical operational bottleneck.

Currently, cohort records are exported from LMS tools into fragmented, unstructured flat text files. The Technical Operations and Systems Administration team must manually ingest these files, write ad-hoc scripts, and adjust file permissions individually to compile employer partner reports. This legacy process introduces several major vulnerabilities:
1. **Data Security & Integrity Risks:** Sensitive learner performance metrics reside in unprotected file directories without role-based access control or audit trails.
2. **Lack of Standardized Configuration Management:** Absence of version control across ingestion scripts leads to silent failures and unrepeatable deployments.
3. **Operational Inefficiency:** Manual verification of hundreds of records wastes valuable engineering hours and delays critical reporting to hiring partners.

---

## 2. Project Scope & Deliverables
The scope of this engagement entails architecting, engineering, securing, and documenting a lightweight, resilient backend system built exclusively with Python standard libraries, SQLite3, Git, and Linux CLI utilities in a WSL environment.

### In-Scope Deliverables:
1. **Software Configuration Management (Git):** Complete Git repository with structured commit history across all development sprints.
2. **Object-Oriented Programming (Python):** `code/models.py` defining base `User` class and polymorphic `Learner` and `Instructor` subclasses with strict boundary and finite score enforcement.
3. **Data Ingestion Engine (`code/main.py`):**
   - Resilient CSV parser for `raw_cohort_data.csv` with whitespace-insensitive header normalization.
   - Strict data casting of assessment scores to finite `float` (`math.isfinite`), strictly intercepting `NaN`, `Infinity`, and `-Infinity`.
   - Idempotent and deterministic ingestion policy using `INSERT ... ON CONFLICT(learner_id) DO UPDATE SET` to preserve record identity without data truncation.
   - Mathematical quality audit mechanism flagging every 10th learner (`processed_valid_counter % 10 == 0`).
   - Fault-tolerant exception handling logging malformed rows without process termination.
   - Mandatory operational activity logging (`logs/application_activity.log`) enforcing immediate abort if log creation fails.
4. **Relational Database (`data/sprints_learners.db`):** Normalized 3NF SQLite relational database containing normalized `cohorts` and `learners` tables, foreign keys, and parameterized query execution to strictly prevent SQL injection.
5. **Operational Activity Logging (`logs/application_activity.log`):** External logging of runtime events, validation warnings, and database transaction summaries.
6. **Linux Security & Administration (`logs/linux_operations.log`):**
   - Package management verification of `sqlite3` via `apt-get` on Ubuntu 26.04.1 LTS (WSL2).
   - Dedicated primary administrative group provisioning (`sprints_ops`, GID: 1003).
   - Hardened permissions with `chmod 750` for scripts/code, `chmod 660` for database and logs, and `chown` for non-root execution.
   - Functional write permission verification for SQLite as non-root operator.
   - Process tracking and CPU/memory resource verification via `ps` and `grep` without error suppression.
7. **Documentation & Presentation Deliverables:**
   - Detailed System Architecture & Implementation Report (`docs/System_Architecture_Report.pdf` & `.md`).
   - Executive Capstone Presentation Deck (`docs/Capstone_Presentation.pdf` & `.md`).
   - Recorded End-to-End Walkthrough (`Demo_Walkthrough.mp4` & `docs/DEMO_SCRIPT.md`).

### Out-of-Scope:
- Heavy third-party web frameworks (e.g., Django, Flask, FastAPI).
- External data manipulation libraries (e.g., Pandas, NumPy).
- Cloud-hosted enterprise databases (e.g., PostgreSQL, Snowflake); strictly native SQLite3.

---

## 3. Success Criteria & Metrics
| Metric / Criteria | Target | Verification Method |
| :--- | :--- | :--- |
| **Ingestion Pipeline Uptime** | Fault-Tolerant Ingestion | Pipeline logs invalid rows, completes entire batch without crashing |
| **Data Normalization** | 3NF Relational Integrity | SQLite schema with foreign keys, unique constraints, and indexes |
| **SQL Injection Prevention** | Parameterized Execution | 100% parameterized queries (`?` placeholders) verified by unit tests |
| **Score Validation Robustness** | Strict Finite Real Numbers | Traps `NaN`, `+Inf`, `-Inf`, and out-of-bounds `[0.0, 100.0]` |
| **Quality Audit Sampling** | 10% Periodic Sample | Modulus operation (`% 10 == 0`) with audit log entries |
| **Linux Security Baseline** | Group-restricted access | Permissions `750`/`660`, Primary Group `sprints_ops` (GID: 1003) |
| **Automated Testing** | Full Test Verification | 22 automated unit & integration tests passed in recorded test run |
| **Reproducibility** | Verified Environment Setup | Linux setup verified in documented WSL2 environment |

---

## 4. Key Assumptions & Constraints
- **Strict Standard Library Constraint:** No pip packages or third-party frameworks for core ingestion logic; standard Python 3.10+ and SQLite3 only.
- **Environment:** Ubuntu Linux on WSL2 with non-root operator account (`sprints_ops`).
- **Data Quality:** The raw input data may contain malformed scores, missing fields, or empty values that must be intercepted gracefully.

---

## 5. Risk Assessment & Mitigation Strategy
| Risk Description | Severity | Likelihood | Mitigation Strategy |
| :--- | :---: | :---: | :--- |
| Malformed or corrupted CSV rows causing parsing crash | High | Medium | Implement comprehensive `try-except` blocks around type casting; log anomalies to `application_activity.log` and continue ingestion. |
| SQL Injection attacks via raw CSV strings | Critical | Low | Strictly enforce parameterized SQL queries (`cursor.execute(sql, params)`); ban string formatting for SQL. |
| Insecure permissions permitting unauthorized data tampering | High | Medium | Enforce Unix permission model: root setup, primary group ownership (`sprints_ops`), `chmod 750` on execution scripts, `chmod 660` on SQLite database and operational logs. |
| Process resource spikes during large cohort batch imports | Medium | Low | Efficient row-by-row streaming generator, benchmarked with `ps aux | grep main.py` monitoring. |

---

## 6. Project Timeline & Sprints
```
Sprint 1 (Days 1-5): Software Configuration Management, System Architecture, Database Schema
Sprint 2 (Days 6-11): Core OOP Models, Ingestion Engine, Modulus Audit, Robust Logging & SQLite Persistence
Sprint 3 (Days 12-14): Linux Hardening, Package Management, Process Monitoring, PDF Reports & Video Walkthrough
```
