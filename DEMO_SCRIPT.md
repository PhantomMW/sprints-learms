# Sprints LEARMS — Capstone Demo Walkthrough Script

**Project:** Learner Assessment & Resource Management System (LEARMS)  
**Presenter:** Mohammed Wael, Junior Solutions Consultant  
**Stakeholder Audience:** Fatima Rashid (Director of Technical Operations) & Sprints Engineering Team  
**Deliverable File:** `Demo_Walkthrough.mp4`  
**Duration:** ~3:45 (Within the 3-5 minute rubric window)  
**Date:** November 2026  

---

## Slide & Scene Timeline Overview

| Time | Scene / Module | Visual Screen | Spoken Narration / Demonstration Focus |
| :---: | :--- | :--- | :--- |
| **0:00 - 0:30** | **1. Welcome & Business Context** | Title Card & Executive Problem Summary | Introduction, acknowledging Sprints rapid growth, explaining the data ingestion bottleneck across regional cohorts. |
| **0:30 - 1:15** | **2. OOP Domain Models (`code/models.py`)** | Code walk: `User`, `Learner`, `Instructor` | Explaining OOP inheritance, polymorphism via `display_profile()`, score casting to float, and letter grade logic. |
| **1:15 - 2:00** | **3. Normalized Relational Database** | ER Diagram & SQLite Schema | Demonstrating 3NF normalization (`Cohorts` and `Learners`), foreign keys, and SQL injection prevention via parameterized queries. |
| **2:00 - 2:45** | **4. Live Batch Ingestion & % 10 Audit** | Terminal execution of `main.py --verify` | Ingesting 45 learners from `raw_cohort_data.csv`, showing modulus trigger on SP-L-1010, 1020, 1030, 1040, and transaction logging. |
| **2:45 - 3:30** | **5. 100% Uptime Exception Handling** | Terminal execution: `--test-edge-cases` | Proving pipeline resilience against malformed float scores, missing columns, and corrupted records without halting execution. |
| **3:30 - 4:15** | **6. Linux Security & Process Telemetry** | WSL Terminal: `ps aux`, `chmod`, `chown` | Demonstrating `sprints_ops` group ownership, octal permissions (`750`/`640`), non-root execution, and memory/CPU telemetry. |
| **4:15 - 4:45** | **7. SQLite CLI Data Verification** | Terminal: `sqlite3 data/sprints_learners.db` | Direct SQL inspection verifying tables, cohort counts, and quality audit rosters. |
| **4:45 - 5:00** | **8. Conclusion & Sign-off** | Final Deliverables & Summary Slide | Recapping successful delivery against all rubric criteria; closing remarks. |

---

## Detailed Scene-by-Scene Presenter Script

### Scene 1: Welcome & Executive Context (0:00 - 0:30)
> *"Hello Fatima and the Sprints technical operations team. I am Mohammed Wael, Junior Solutions Consultant. Today, I am proud to walk you through the completed Learner Assessment and Resource Management System—or LEARMS.*  
> *As Sprints scales its cohorts across the MENA region, the legacy method of juggling fragmented text files, manual permission edits, and disjointed scripts introduced severe data integrity and security bottlenecks. LEARMS delivers an automated, secure, Python-driven SQLite backend deployed in a hardened Linux environment to permanently solve this problem."*

### Scene 2: Object-Oriented Domain Models (0:30 - 1:15)
> *"Let's examine `code/models.py`. In accordance with our OOP requirements, we architected a base `User` class encapsulating core identity: user ID, full name, role, email, and validation logic.*  
> *We extend `User` into specialized subclasses: `Learner` and `Instructor`.*  
> *Notice our polymorphic implementation of `display_profile()`. When called on a Learner, it dynamically formats their academic record, prints their assessment score to two decimal places, evaluates their letter grade band, and displays an attention-grabbing audit badge if flagged.*  
> *When called on an Instructor, it highlights their teaching specialization and active cohort assignments. This polymorphism ensures our data pipeline treats actors through a clean, unified interface."*

### Scene 3: Normalized Relational Database Architecture (1:15 - 2:00)
> *"Turning to data persistence in `data/sprints_learners.db`: rather than maintaining unstandardized flat files, we normalized the schema to Third Normal Form.*  
> *We separated cohort metadata into a parent `Cohorts` table with a unique constraint and track categorization, linked to a child `Learners` table through a foreign key.*  
> *We enable `PRAGMA foreign_keys = ON;` upon every connection to guarantee referential integrity. Most importantly, every single database query utilizes parameterized execution with question-mark placeholders—strictly preventing any SQL injection attacks from untrusted CSV inputs."*

### Scene 4: Live Data Ingestion & Modulus Quality Auditing (2:00 - 2:45)
> *"Now let's see the engine in action. In the terminal, we execute `python3 code/main.py --verify`.*  
> *The pipeline parses `data/raw_cohort_data.csv`, casts assessment scores to Python floats, and resolves cohort foreign keys.*  
> *Here is the mathematical quality audit mechanism: every 10th processed valid learner is flagged for employer partner review using `learner_counter % 10 == 0`.*  
> *In our 45-learner production dataset, exactly 4 learners—Hadeer Mostafa, Dina Salah, Laila Gohar, and Riham Shafik—are flagged, recorded in the database, and stamped in `logs/application_activity.log` along with the transaction duration of under 15 milliseconds."*

### Scene 5: 100% Ingestion Uptime & Edge Case Recovery (2:45 - 3:30)
> *"Fatima emphasized in our discovery call that corrupted scores or malformed rows must not break the pipeline.*  
> *To prove our 100% uptime acceptance criteria, we run `python3 code/main.py --test-edge-cases` against a corrupted dataset containing non-numeric strings, negative grades, and missing keys.*  
> *Notice how our granular try-except blocks intercept each anomaly, log descriptive warnings to the dead-letter log, and continue ingesting all remaining valid records without crashing. The transaction commits with 100% pipeline uptime."*

### Scene 6: Linux Systems Administration & Process Telemetry (3:30 - 4:15)
> *"Next, we inspect the hosting Linux environment inside WSL2 Ubuntu.*  
> *As documented in `logs/linux_operations.log`, SQLite3 was provisioned via `apt-get`.*  
> *We established the `sprints_ops` administrative group and applied least-privilege permissions: `chmod 750` on execution scripts, `chmod 640` on the SQLite database, and `chmod 660` on logs. This ensures daily operations run securely under non-root user `mw851`.*  
> *Furthermore, using `ps aux | grep main.py` and `ps -o %cpu,%mem,vsz,rss`, we monitored active execution under simulated load. Telemetry verifies an ultra-lean memory footprint under 28 megabytes RSS and single-threaded CPU efficiency."*

### Scene 7: SQLite CLI Database Verification (4:15 - 4:45)
> *"Let's verify the database directly via the SQLite3 CLI:*  
> *Running `SELECT COUNT(*) FROM learners;` returns exactly 45 learners.*  
> *`SELECT COUNT(*) FROM cohorts;` confirms 5 distinct normalized tracks.*  
> *And querying `WHERE is_audited = 1` immediately extracts our random 10% quality audit sample for employer partners."*

### Scene 8: Conclusion & Next Steps (4:45 - 5:00)
> *"In summary, LEARMS successfully fulfills 100% of the functional and non-functional requirements across all three sprints.*  
> *All deliverables—the source code, SQLite database, Linux operation logs, PDF Architecture Report, Presentation Deck, and Git repository—are ready for production deployment.*  
> *Thank you, and I look forward to your questions."*
