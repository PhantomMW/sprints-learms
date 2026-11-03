# System Architecture & Implementation Report
**Project:** Learner Assessment & Resource Management System (LEARMS)
**Organization:** Sprints
**Prepared By:** [Your Name/Title - e.g., Junior Solutions Consultant]
**Date:** [Date]

---

## 1. Executive Summary
Provide a brief overview of the LEARMS implementation. Discuss how this Python-driven backend application and its underlying SQLite database resolve the Sprints Technical Operations team's bottlenecks regarding fragmented raw cohort files, security vulnerabilities, and lack of standardized version control.

> *[Draft your executive summary here...]*

---

## 2. Software Configuration Management: Git Strategy
Describe the version control strategy employed during the two-week capstone engagement. 

### 2.1 Repository Structure
Detail the directory structure of the repository (e.g., `code/`, `data/`, `logs/`, `docs/`).

> *[Detail repository structure here...]*

### 2.2 Commit Workflow
Explain your commit frequency and naming conventions. How did you ensure logical segmentation of the application components (e.g., separating OOP definitions from database operations)?

> *[Explain your Git workflow and commit strategy here...]*

---

## 3. Python Object-Oriented Programming (OOP) Models
LEARMS leverages strict OOP principles to encapsulate business logic. Detail the classes implemented in your `code/models.py` file.

### 3.1 Base Class: `User`
Describe the attributes and methods of the base `User` class.

> *[Describe the User class here...]*

### 3.2 Subclasses & Polymorphism: `Learner` and `Instructor`
Explain how the `Learner` and `Instructor` classes inherit from `User`. Provide examples of polymorphism—specifically, which methods were overridden in the subclasses and why.

> *[Describe the subclasses and polymorphism implementation here...]*

---

## 4. Database Schema Design (SQLite)
To support Sprints' scaling cohort sizes, raw assessment data is normalized into an SQLite database (`sprints_learners.db`).

### 4.1 Entity-Relationship Layout
Describe the normalized tables (`Cohorts` and `Learners`). How are they related (e.g., Foreign Keys)?

> *[Describe the table structures and relationships here...]*

### 4.2 Data Dictionary
Detail the column structures for both tables, ensuring that assessment scores are explicitly cast to the appropriate data type (e.g., `FLOAT`).

**Table: Cohorts**
*   `cohort_id` (Type, Primary Key)
*   *[Add additional fields...]*

**Table: Learners**
*   `learner_id` (Type, Primary Key)
*   `assessment_score` (FLOAT)
*   *[Add additional fields...]*

---

## 5. Application Logic & Data Flow
Detail the core operations executed by `code/main.py`.

### 5.1 Data Ingestion & Transformation
Explain how `raw_cohort_data.csv` is parsed. Discuss the specific Python logic used to cast data types. 

> *[Explain parsing logic here...]*

### 5.2 Quality Audit Flagging
Describe the modulus operation (`% 10`) implemented to flag every 10th learner for a random quality audit by Sprints employer partners.

> *[Explain the modulus audit logic here...]*

### 5.3 Exception Handling & Logging
Detail the robust `try-except` blocks wrapping file I/O and database connections. How does the application prevent runtime crashes, and what specific transaction summaries are written to `application_activity.log`?

> *[Detail your exception handling and file I/O logging strategy here...]*

---

## 6. Linux Configuration & Process Management
The LEARMS application operates within a strictly configured Linux/WSL environment. Document the system administration operations performed.

### 6.1 Package Management
Document the commands used via `apt-get` (or equivalent) to ensure `sqlite3` and other essential dependencies were installed.

> *[Document package management commands here...]*

### 6.2 Security & File Permissions
Explain how you used `chmod` and `chown` to restrict folder/file access. How did you ensure the application directory's primary group is set for secure execution by Sprints system administrators without requiring root/sudo privileges?

> *[Document your chown and chmod configurations here...]*

### 6.3 Process Monitoring
Detail the CLI commands utilized (`ps` combined with `grep`) to monitor the active Python application process. How did you verify the memory and CPU state?

> *[Document your process monitoring commands here...]*

---

## 7. Conclusion & Deployment Sign-off
Summarize the successful delivery of LEARMS and how it meets the success criteria laid out by the Director of Technical Operations. Include links to the `logs/linux_operations.log` and the recorded `Demo_Walkthrough.mp4`.

> *[Draft your conclusion here...]*