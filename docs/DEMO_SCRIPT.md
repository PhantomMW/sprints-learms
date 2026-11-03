# Sprints LEARMS — Demo Walkthrough Video Narration Script

**Project Title:** Learner Assessment & Resource Management System (LEARMS)  
**Client Organization:** Sprints  
**Lead Engineer / Presenter:** Mohammed Wael (Junior Solutions Consultant)  
**Target Video Duration:** ~4 Minutes (1080p Full HD)  
**Accompanying Video Artifact:** `Demo_Walkthrough.mp4`  

---

## Executive Introduction (00:00 – 00:30)
**Visual:** Title slide featuring Sprints logo, project charter banner, technical stack pills (Python, SQLite3, Git, WSL2 Ubuntu, Linux CLI), and presenter details.

**Spoken Narration:**
> "Hello everyone, and welcome to the capstone project presentation and technical demonstration of the **Learner Assessment & Resource Management System (LEARMS)**, engineered for **Sprints**.
>
> Sprints delivers high-impact EdTech learning pathways across Data Science, AI, Web Development, Cloud Computing, and Cybersecurity. As student cohort sizes scale exponentially, managing learner performance data across disparate CSV exports has become a severe operational bottleneck. 
>
> Over this intensive two-week engagement, I have architected and deployed a secure, production-grade backend application using strictly standard libraries—no third-party frameworks, no Pandas, no Django. Today, I am excited to walk you through the end-to-end architecture, from Object-Oriented design and relational database persistence to Linux security hardening and telemetry monitoring."

---

## Chapter 1: Software Configuration Management & Git Architecture (00:30 – 01:00)
**Visual:** VS Code terminal displaying Git commit ledger (`git log --oneline --graph`), semantic commit tags (`chore:`, `feat:`, `ops:`, `release:`), and the clean repository structure.

**Spoken Narration:**
> "We begin with **Sprint 1: Software Configuration Management**. An enterprise project demands rigorous version control. 
>
> The local repository was initialized with an industry-standard directory hierarchy separating application code, data, logs, deployment scripts, tests, and documentation. 
>
> Every commit adheres strictly to the Conventional Commits standard. Key milestones are tagged—culminating in our production baseline release, which is fully tracked and synchronized with our remote repository."

---

## Chapter 2: Object-Oriented Domain Modeling & Polymorphism (01:00 – 01:30)
**Visual:** Code editor opening `code/models.py`, highlighting the base `User` class and the polymorphic subclasses `Learner` and `Instructor`, with method overriding of `display_profile()` and `get_details()`.

**Spoken Narration:**
> "Moving to **Sprint 2: Object-Oriented Programming in Python**, we modeled the Sprints educational ecosystem inside `code/models.py`.
>
> At the foundation sits our abstract base class `User`, which encapsulates user identity, email derivation, and profile validation. 
>
> We then subclass `Learner` and `Instructor`. Polymorphism is demonstrated through method overriding: `Learner.display_profile()` computes the learner's letter grade based on standardized assessment thresholds, highlights audit badges, and strictly validates that assessment scores are finite real numbers—shielding our database from `NaN` and `Infinity` traps.
>
> Meanwhile, `Instructor.display_profile()` formats teaching specializations and assigned cohort rosters."

---

## Chapter 3: Resilient Data Ingestion Pipeline & Fault Tolerance (01:30 – 02:10)
**Visual:** Execution of `python3 code/main.py`, showing terminal logging stream, whitespace header normalization, modulus 10 sampling badges, and transaction summary.

**Spoken Narration:**
> "Next is the heart of the backend: the **Data Ingestion Engine** in `code/main.py`.
>
> The pipeline streams raw cohort CSV data without loading massive files into memory. It applies robust header normalization to handle whitespace or delimiter variations.
>
> In accordance with Sprints business criteria, assessment scores are cast to `float` and verified with `math.isfinite()`. To ensure fault-tolerant, uninterrupted batch processing, malformed or empty rows are gracefully intercepted using granular `try-except` blocks, logged as operational warnings, and skipped without halting the pipeline.
>
> Notice the **Modulus 10 Sampling Mechanism**: every 10th valid learner is automatically flagged with an audit indicator (`% 10 == 0`) and recorded in our system audit ledger for quality review."

---

## Chapter 4: Relational SQLite Database & Parameterized Execution (02:10 – 02:50)
**Visual:** Terminal querying `data/sprints_learners.db` via SQLite CLI (`sqlite3`), inspecting 3NF normalized tables (`cohorts`, `learners`, `system_audit_log`), and running verification queries.

**Spoken Narration:**
> "For data persistence, we engineered `data/sprints_learners.db` in full compliance with **Third Normal Form (3NF)**.
>
> The schema enforces relational integrity with foreign keys linking learners to their respective cohorts. Crucially, our ingestion query uses parameterized statement binding (`?` placeholders) with deterministic upsert semantics: `INSERT INTO learners (...) ON CONFLICT(learner_id) DO UPDATE SET`.
>
> Parameterized SQL queries mitigate SQL injection risks by separating SQL statements from user-supplied data, while ensuring idempotent, repeat-safe re-runs that preserve row identity without data truncation.
>
> As shown on screen, querying the database confirms that 45 learners across 5 tech cohorts are stored, with exactly 4 learners flagged for quality audit sampling."

---

## Chapter 5: Linux Systems Administration, Groups & Permissions (02:50 – 03:25)
**Visual:** Review of `scripts/setup_linux_env.sh` and `logs/linux_operations.log`, showing `apt-get` installation of SQLite3 on Ubuntu 26.04.1 LTS, user management, and `ls -la` permission matrix.

**Spoken Narration:**
> "In **Sprint 3: Linux Systems Administration**, we transitioned to an Ubuntu WSL2 environment.
>
> Using native package management, `sqlite3` and `libsqlite3-dev` were installed and verified. To adhere to the principle of least privilege, we created the `sprints_ops` administrative group and configured it as the **Primary Group** (dynamically assigned `gid=1003` in our WSL2 test environment; note that GID numbers vary across Linux host environments) for our non-root operator `mw851`.
>
> We then applied a strict permission matrix: `chmod 750` for application code and shell scripts, `chmod 660` for the SQLite database and logs to allow group-write operations, and `chmod 640` for documentation.
>
> Functional write access for the non-root operator was conclusively verified by executing real write transactions inside SQLite."

---

## Chapter 6: Active Process Telemetry & Telemetry Monitoring (03:25 – 03:55)
**Visual:** Execution of `scripts/monitor_process.sh`, displaying `ps aux | grep main.py`, process table headers, PID, %CPU, %MEM, and Resident Set Size (RSS).

**Spoken Narration:**
> "To verify operational health under real workloads, we executed `scripts/monitor_process.sh`.
>
> Using native Linux utilities `ps` and `grep`, we monitored the active ingestion process under simulated load. The telemetry displays:
> - **Operator & Group:** `mw851` executing under primary group `sprints_ops`.
> - **CPU Utilization:** 26.0% to 27.2% during active parsing.
> - **Memory Footprint:** Steady-state Resident Set Size (RSS) under 28 MB, demonstrating extreme efficiency.
> - **Process Exit Code:** The monitoring script strictly tracks process exit status, confirming clean termination with exit code 0."

---

## Chapter 7: Automated Test Suite & Capstone Deliverables (03:55 – 04:15)
**Visual:** Running `python -m unittest discover -s tests -v`, showing 24/24 tests passing in ~0.38s, followed by the final slide showing the repository, documentation PDFs, and submission archive.

**Spoken Narration:**
> "Finally, software quality is guaranteed by our comprehensive test suite in `tests/`. 
>
> 24 automated unit and integration tests validate domain models, parameterized SQL injection defense, duplicate ID updates, database migration deduplication, NaN and Infinity rejection, column count mismatches, invalid status rejection, header-only CSV processing, and SQLite safe write permissions—running in under 0.4 seconds with all tests verified.
>
> All project deliverables—the complete Git repository, database file, Linux terminal logs, System Architecture Report PDF, Presentation Deck, and this walkthrough—are packaged and ready for deployment.
>
> Thank you for your time, and I look forward to your questions and evaluation."
