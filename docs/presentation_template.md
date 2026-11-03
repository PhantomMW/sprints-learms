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
**Presenter:** [Insert Your Name]
**Role:** Junior Solutions Consultant
**Organization:** Sprints
**Date:** [Insert Date]

---

# 1. Executive Summary
## Bridging Learning and Employment Efficiently

- **The Challenge:** [Describe the current bottleneck: Sprints' manual ingestion of fragmented text files, insecure folder permissions, and lack of version control.]
- **The Solution:** [Provide a high-level overview of LEARMS — a unified, secure, Python-driven SQLite backend application.]
- **Business Impact:** [Explain how this system reduces sysadmin overhead, mitigates data security risks, and provides standardized reporting for Sprints' employer partners in the MENA region.]

---

# 2. System Architecture
## Robust, Standardized, and Secure

- **Application Core:** [Describe the use of standard Python libraries to parse `raw_cohort_data.csv`.]
- **Data Persistence:** [Describe the transition from scattered text files to a centralized SQLite database (`sprints_learners.db`).]
- **Infrastructure:** [Mention the strictly configured Linux (WSL) environment and the use of Git for version-controlled deployments.]
- **System Flow Diagram:** 
  *[Placeholder: Insert a diagram or bulleted flow showing CSV -> Python Parser -> SQLite DB -> Secure Linux Directory]*

---

# 3. Database Schema
## Relational Integrity for Cohort Data

- **Target Database:** `sprints_learners.db`
- **Tables & Normalization:**
  - **Cohorts Table:** [List your columns here, e.g., `cohort_id` (PK), `program_name`, `start_date`.]
  - **Learners Table:** [List your columns here, e.g., `learner_id` (PK), `name`, `assessment_score` (Float), `cohort_id` (FK).]
- **Design Rationale:** [Briefly explain how this one-to-many relationship standardizes learner data and eliminates the anomalies found in the previous flat files.]

---

# 4. Object-Oriented (OOP) Design
## Encapsulating Sprints' Business Logic

- **Base Class (`User`):**
  - *Attributes:* [e.g., `name`, `email`, `role`]
  - *Methods:* [e.g., `display_profile()`]
- **Subclasses (`Learner` & `Instructor`):**
  - *Learner-specific logic:* [Explain how `display_profile()` is overridden to display float assessment scores and audit status.]
  - *Instructor-specific logic:* [Explain how the method is overridden to display assigned teaching cohorts.]
- **Polymorphism:** [Define how utilizing a shared method name across different user types streamlines the Python parsing logic.]

---

# 5. Linux Security Configurations
## Protecting Learner Data

- **Objective:** Secure the LEARMS infrastructure without relying on root privileges for daily execution.
- **Package Management:** [Explain the terminal steps taken using `apt-get` to install and verify `sqlite3`.]
- **File Ownership (`chown`):** [Detail how the primary group of the application directory was assigned to the Sprints technical operations group.]
- **Access Permissions (`chmod`):** [Detail the exact permission octal (e.g., `750` or `770`) applied to ensure only authorized sysadmins can read/execute the Python parser and access the SQLite database.]

---

# 6. Process Monitoring & Operations
## Ensuring High Availability

- **Execution Logging:** [Discuss how script events and database transactions are securely appended to `application_activity.log`.]
- **Active Process Tracking:** [Explain the Linux CLI commands used during execution: using `ps` piped to `grep`.]
- **Resource Verification:** [Describe how monitoring CPU and memory states ensures the Python parsing process doesn't bottleneck Sprints' host servers during massive cohort imports.]

---

# 7. Exception Handling & Quality Auditing
## Building a Resilient Pipeline

- **Runtime Resilience:** [Detail the `try-except` blocks surrounding all file I/O and database connection logic to intercept missing files or locked databases.]
- **Data Type Casting:** [Explain the process of scrubbing raw CSV data and enforcing `float` types for assessment scores.]
- **Random Quality Audits:** [Explain the mathematical logic—using the modulus operation (`learner_id % 10 == 0`)—to flag exactly 10% of users for Sprints' manual quality assurance reviews.]

---

# 8. Next Steps & Future Enhancements
## Scaling for the Future

- **Automation:** [Insert idea: Implement Linux `cron` jobs to automatically execute `main.py` at midnight for nightly cohort syncs.]
- **Advanced Reporting:** [Insert idea: Build a REST API layer over `sprints_learners.db` to serve real-time analytics to employer partners.]
- **CI/CD Integration:** [Insert idea: Expand current Git version control into automated deployment pipelines for Sprints' engineering team.]

---

# 9. Conclusion & Q&A
## Thank You

- **Summary:** By replacing disjointed manual scripts with LEARMS, Sprints now possesses a secure, OOP-driven, and highly auditable backend pipeline ready to scale alongside growing cohort sizes.
- **Deliverables Completed:** Version Control (Git), Database (SQLite), Backend (Python), Infrastructure (Linux CLI).
- **Questions?** [Open the floor for questions from the Director of Technical Operations and Engineering team]