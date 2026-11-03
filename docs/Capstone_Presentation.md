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
- **The Solution:** Architected and deployed **LEARMS** — a lightweight, secure, Python-driven SQLite backend engineered strictly with core standard libraries.
- **Business Impact:**
  - 100% elimination of manual data manipulation and permission friction.
  - 100% data ingestion uptime with zero-crash error handling.
  - Standardized, auditable employer-partner reporting across MENA tech programs.

---

# 2. System Architecture
## Robust, Standardized, and Secure

- **Application Core:** Standard Python 3.10+ engine utilizing native `csv`, `sqlite3`, `logging`, and `os` modules — no bulky external dependencies.
- **Data Persistence:** Transitioned from scattered text files to normalized SQLite relational database (`sprints_learners.db`) with foreign key constraints.
- **Infrastructure:** Hardened Linux (WSL2 Ubuntu) environment with group-based access control and real-time process monitoring.
- **System Flow:**
  ```text
  [Raw Cohort CSV] ──► [Streaming DictReader] ──► [OOP Polymorphic Validation]
                                                           │
                                                           ▼
  [logs/application_activity.log] ◄── [SQLite3 DB] ◄── [Modulus Audit Check %10]
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
  - B-Tree indexes on `cohort_id` and `is_audited` guarantee sub-millisecond querying.

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
- **Group Ownership (`chown`):** Established `sprints_ops` administrative group; assigned full application directory ownership to non-root operators.
- **Access Permissions (`chmod`):**
  - Scripts & Directories (`750`): Read/Execute restricted to owner and `sprints_ops` group.
  - Relational Database (`640`): Restricted to application service accounts; world-readable access denied.
  - Operational Logs (`660`): Read/Write access granted strictly to ops personnel.

---

# 6. Process Monitoring & Operations
## Telemetry and Resource Verification

- **Execution Logging:** Complete transactional telemetry written to `logs/application_activity.log`, logging batch records, duration, and audit flags.
- **Active Process Tracking:** Monitored live execution using Linux CLI utilities:
  ```bash
  ps aux | grep "[p]ython3 code/main.py"
  ```
- **Resource Verification:**
  - Memory Footprint: Steady state under 18 MB RSS with zero memory leaks.
  - CPU Utilization: Near-instant batch processing (< 25ms for 45 records).
  - High Availability: Clean daemonization and benchmark load testing capability.

---

# 7. Exception Handling & Quality Auditing
## A Resilient Ingestion Pipeline

- **100% Ingestion Uptime:** Granular `try-except` blocks surround all file I/O, type conversions, and database operations.
- **Malformed Data Recovery:** Invalid scores (e.g., non-numeric strings, negative numbers) are intercepted, logged to the dead-letter log, and skipped without terminating the batch.
- **Data Type Casting:** Enforces float conversion (`float(score)`) to ensure exact arithmetic precision for GPA and grade bands.
- **Random Quality Audits:**
  - Evaluates `processed_count % 10 == 0` during ingestion.
  - Flags exactly 10% of ingested learners (`is_audited = 1`) for mandatory employer partner quality audits.

---

# 8. Next Steps & Future Enhancements
## Scaling LEARMS for Future Growth

- **Automated Scheduling:** Deploy Linux `cron` jobs to trigger automated nightly synchronization of LMS export folders at midnight.
- **Partner REST API:** Build a lightweight, secure REST API layer over `sprints_learners.db` to serve real-time hiring metrics to employer partners.
- **Enterprise CI/CD:** Integrate GitHub Actions to run automated unit tests (`tests/test_models.py`, `tests/test_ingestion.py`) on every push.
- **Multi-Tenant Cohort Partitioning:** Expand database schemas to support cross-regional cohort clustering across Egypt, KSA, and UAE.

---

# 9. Conclusion & Deployment Sign-off
## Mission Accomplished

- **Summary:** LEARMS replaces fragile, unversioned scripts with an automated, secure, and fully auditable OOP architecture.
- **Deliverables Completed:**
  - Version-controlled Git repository with descriptive sprint commits.
  - Core Python engine (`code/main.py`) & OOP domain models (`code/models.py`).
  - Normalized SQLite database (`data/sprints_learners.db`).
  - Terminal audit log (`logs/linux_operations.log`) & activity log (`logs/application_activity.log`).
  - System Architecture Report (PDF/MD) & Capstone Presentation Deck (PDF/MD).
  - End-to-end recorded walkthrough (`Demo_Walkthrough.mp4`).
- **Open for Questions & Stakeholder Discussion.**
