---
marp: true
theme: default
class: lead
paginate: true
backgroundColor: #f8fafc
color: #0f172a
---

# Sprints Learner Assessment & Resource Management System (LEARMS)
## Capstone Project Final Presentation
**Presenter:** Mohammed Wael  
**Role:** Junior Solutions Consultant  
**Organization:** Sprints  
**Date:** November 2026  
**Primary Stakeholder:** Fatima Rashid, Director of Technical Operations  

---

# 1. Executive Summary
## Bridging Learning and Employment Efficiently

- **The Challenge:** Rapid scaling of tech cohorts led to a critical operational bottleneck. Learner assessment data was fragmented across raw text files, ingested manually with ad-hoc scripts, and held insecure folder permissions without version control.
- **The Solution:** Architected and deployed **LEARMS** — an automated, secure, Python-driven SQLite backend engineered strictly with core standard libraries.
- **Business Impact:**
  - Automates end-to-end CSV ingestion, relational storage, and validation, eliminating manual file editing and script execution.
  - Fault-tolerant ingestion pipeline with zero-crash error handling and dead-letter activity logging.
  - Standardized, auditable employer-partner reporting across MENA tech programs.

---

# 2. System Architecture
## Robust, Standardized, and Secure

- **Application Core:** Standard Python 3.10+ engine utilizing native `csv`, `sqlite3`, `logging`, and `os` modules — no bulky external dependencies.
- **Data Persistence:** Transitioned from scattered text files to normalized SQLite relational database (`sprints_learners.db`) with foreign key constraints.
- **Infrastructure:** Hardened Linux (WSL2 Ubuntu) environment with Primary Group isolation (`sprints_ops`) and real-time process monitoring.
- **System Flow:**
  ```text
  [Raw Cohort CSV] ──► [Header Normalization] ──► [OOP Polymorphic Validation]
                                                           │
                                                           ▼
  [logs/application_activity.log] ◄── [ON CONFLICT DB Update] ◄── [Periodic Audit %10]
  ```

---

# 3. Database Schema Design
## Relational Integrity for Scaling Cohorts

- **Target Database:** `data/sprints_learners.db` (Normalized 3NF Schema)
- **Relational Tables:**
  - **Cohorts Table:** `cohort_id` (PK), `cohort_name` (UNIQUE), `program_track`, `created_at`.
  - **Learners Table:** `learner_id` (PK), `full_name`, `cohort_id` (FK), `assessment_score` (REAL/Float), `enrollment_status`, `is_audited` (Boolean), `created_at`.
- **Relational Integrity & Defense:**
  - `PRAGMA foreign_keys = ON;` enforces strict referential consistency.
  - 100% Parameterized queries (`?` syntax) eliminates all SQL injection risks.
  - `ON CONFLICT(learner_id) DO UPDATE SET` ensures idempotency and preserves existing row identity during repeated ingestion batches.

---

# 4. Object-Oriented (OOP) Design
## Encapsulating Sprints' Domain Logic

- **Base Class (`User`):**
  - Attributes: `user_id`, `full_name`, `email`, `role`, `created_at`.
  - Shared Methods: `display_profile()`, `get_details()`, `validate()`.
- **Subclasses (`Learner` & `Instructor`):**
  - **`Learner` Subclass:** Extends `User` with `cohort_name`, float `assessment_score`, `enrollment_status`, and `is_audited`. Overrides `display_profile()` to showcase letter grades and audit badges.
  - **`Instructor` Subclass:** Extends `User` with `specialization` and `assigned_cohorts`. Overrides `display_profile()` to list teaching assignments.
- **Polymorphism in Action:** Unified interface allows the ingestion engine to process diverse user roles transparently while executing specialized business rules.

---

# 5. Linux Security Configurations
## Protecting Learner Records in Production

- **Objective:** Secure the LEARMS infrastructure without relying on root privileges for daily execution.
- **Package Management:** Installed and verified `sqlite3` via `apt-get` within WSL2 Ubuntu, logging output to `linux_operations.log`.
- **Primary Group (`usermod -g`):** Configured `sprints_ops` (GID: 1003) as the operator's primary group, confirmed via `id mw851`.
- **Access Permissions (`chmod`):**
  - Scripts & Directories (`750`): Read/Execute restricted to owner and `sprints_ops` group.
  - Database & Data Files (`660`): Read/Write granted to `sprints_ops` primary group, world-readable access denied.
  - Operational Logs (`660`): Read/Write access granted strictly to ops personnel.

---

# 6. Process Monitoring & Operations
## Telemetry and Resource Verification

- **Execution Logging:** Complete transactional telemetry written to `logs/application_activity.log`, logging batch records, duration, and audit flags.
- **Active Process Tracking:** Monitored live execution using Linux CLI utilities:
  ```bash
  ps -p $PID -o pid,ppid,user,group,%cpu,%mem,vsz,rss,stat,start,time,comm
  ```
- **Resource Verification:**
  - Executing Operator: `USER: mw851 | GROUP: sprints_ops` (Primary group verified).
  - Memory Footprint: Steady state under 20.3 MB RSS with zero memory leaks.
  - CPU Utilization: Near-instant batch processing (< 10ms for 45 records).

---

# 7. Exception Handling & Quality Auditing
## A Resilient Ingestion Pipeline

- **Fault-Tolerant Pipeline:** Granular `try-except` blocks surround all file I/O, type conversions, and database operations.
- **Malformed Data Recovery:** Invalid scores (e.g., non-numeric strings, negative numbers) are intercepted, logged to the dead-letter log, and skipped without terminating the batch.
- **Fail-Safe Activity Logging:** `configure_logger()` raises a fatal runtime error if the operational activity log cannot be created, ensuring full traceability.
- **Automated Periodic Quality Audit Sampling:**
  - Evaluates `processed_valid_count % 10 == 0` during ingestion.
  - Systematically selects every 10th learner (`is_audited = 1`) for mandatory employer partner quality audits.

---

# 8. Testing & Validation Matrix
## Rigorous Automated Test Suite (23/23 Passed)

- **Schema & SQL Defense:** Foreign key integrity & SQL injection payload neutralization verified.
- **Mathematical Rigor & Edge Cases:**
  - `NaN`, `+Infinity`, and `-Infinity` score values strictly rejected via `math.isfinite()`.
  - Duplicate Learner ID (`ON CONFLICT DO UPDATE`) and system audit log idempotency verified without record duplication.
  - Automated legacy database migration deduplication verified prior to unique index creation.
  - Column count mismatch detection (fewer or extra columns rejected without crashing).
  - Invalid enrollment statuses strictly rejected rather than silently altered.
  - Repeated Ingestion Idempotency verified.
  - 0-byte and Header-Only CSVs detected and processed cleanly.
  - Header Normalization (whitespace, casing, dashes) verified.
  - Non-UTF8 CSV Binary Encoding Trapping verified.
  - Unwritable Log Permission Failure verified.
  - Functional SQLite Group Write Transaction verified with safe dynamic probe tables and guaranteed cleanup.
- **Execution Speed:** 23 automated tests executed and passing in under 0.40 seconds.

---

# 9. Next Steps & Future Enhancements
## Scaling for the Future

- **Automation:** Implement Linux `cron` jobs to automatically execute `main.py` at midnight for nightly cohort syncs.
- **Advanced Reporting:** Build a lightweight REST API layer over `sprints_learners.db` to serve real-time analytics to employer partners.
- **CI/CD Integration:** Expand current Git version control into automated deployment pipelines with GitHub Actions.
- **Multi-Tenant Regional Scaling:** Partition cohort schemas across MENA tech hubs (Egypt, KSA, UAE).

---

# 10. Conclusion & Q&A
## Mission Accomplished

- **Summary:** By replacing disjointed manual scripts with LEARMS, Sprints now possesses a secure, OOP-driven, and highly auditable backend pipeline ready to scale alongside growing cohort sizes.
- **Deliverables Completed:** Version Control (Git), Database (SQLite), Backend (Python), Infrastructure (Linux CLI).
- **Questions?** Open the floor for questions from the Director of Technical Operations and Engineering team.
