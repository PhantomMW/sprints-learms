"""
Learner Assessment & Resource Management System (LEARMS)
Module: code.models
Description: Object-Oriented Domain Models encapsulating Sprints business logic,
             user profiles, and polymorphic behaviors.
Author: Mohammed Wael (Junior Solutions Consultant)
Organization: Sprints
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone


class User:
    """
    Base User class establishing the shared contract for all actors
    within the Sprints educational ecosystem.

    Attributes:
        user_id (str): Unique enterprise stakeholder identifier.
        full_name (str): Full legal name of the user.
        email (str): Contact email address.
        role (str): System access role (e.g., 'User', 'Learner', 'Instructor', 'Admin').
        created_at (str): ISO 8601 string timestamp of profile creation.
    """

    def __init__(
        self,
        user_id: str,
        full_name: str,
        email: Optional[str] = None,
        role: str = "User",
        created_at: Optional[str] = None,
    ) -> None:
        """
        Initialize a base User instance with input validation.

        Args:
            user_id: Unique identifier for the user.
            full_name: Full name of the user.
            email: Optional email address. Defaults to auto-generated format if None.
            role: The stakeholder role within the Sprints platform.
            created_at: Optional timestamp string. Defaults to current UTC time.
        """
        self.user_id = str(user_id).strip()
        self.full_name = str(full_name).strip()
        self.role = str(role).strip()
        self.created_at = created_at or datetime.now(timezone.utc).isoformat()

        # Derive standardized email if not explicitly provided
        if email:
            self.email = str(email).strip().lower()
        else:
            sanitized_name = self.full_name.lower().replace(" ", ".")
            self.email = f"{sanitized_name}@sprints.ai"

    def validate(self) -> bool:
        """
        Validate base user invariants.

        Returns:
            bool: True if user attributes meet minimum validation criteria, False otherwise.
        """
        if not self.user_id or not self.full_name:
            return False
        return True

    def display_profile(self) -> str:
        """
        Polymorphic base method to render a standardized user profile.

        Returns:
            str: Multi-line formatted string representing base user profile.
        """
        return (
            f"--- [User Profile: {self.role}] ---\n"
            f"ID         : {self.user_id}\n"
            f"Name       : {self.full_name}\n"
            f"Email      : {self.email}\n"
            f"Role       : {self.role}\n"
            f"Created At : {self.created_at}\n"
            f"---------------------------------"
        )

    def get_details(self) -> Dict[str, Any]:
        """
        Serialize user properties into a dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation of the user entity.
        """
        return {
            "user_id": self.user_id,
            "full_name": self.full_name,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at,
        }

    def __repr__(self) -> str:
        """Developer-friendly string representation."""
        return f"<User(user_id='{self.user_id}', full_name='{self.full_name}', role='{self.role}')>"

    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"{self.full_name} ({self.user_id}) - Role: {self.role}"


class Learner(User):
    """
    Subclass representing upskilling talent enrolled across Sprints cohorts.
    Inherits from User and overrides display_profile and get_details to demonstrate
    polymorphism.

    Attributes:
        cohort_name (str): Name of the assigned tech cohort.
        assessment_score (float): Assessment score cast strictly to float.
        enrollment_status (str): Current enrollment condition ('Active', 'Graduated', 'Dropped').
        is_audited (bool): Audit flag indicating selection for quality review (modulus check).
    """

    def __init__(
        self,
        learner_id: str,
        full_name: str,
        cohort_name: str,
        assessment_score: float,
        enrollment_status: str = "Active",
        is_audited: bool = False,
        email: Optional[str] = None,
        created_at: Optional[str] = None,
    ) -> None:
        """
        Initialize a Learner entity with strict type enforcement.

        Args:
            learner_id: Unique learner identifier (e.g., 'SP-L-1001').
            full_name: Learner's full name.
            cohort_name: Name of the cohort (e.g., 'Data Science Cohort 5').
            assessment_score: Raw or parsed assessment score, cast to float.
            enrollment_status: Status ('Active', 'Graduated', 'Dropped').
            is_audited: Boolean flag set by modulus operation (% 10 == 0).
            email: Optional email address.
            created_at: Optional timestamp string.
        """
        # Call base class constructor with role='Learner'
        super().__init__(
            user_id=learner_id,
            full_name=full_name,
            email=email,
            role="Learner",
            created_at=created_at,
        )

        self.cohort_name = str(cohort_name).strip()
        self.assessment_score = float(assessment_score)
        self.enrollment_status = str(enrollment_status).strip()
        self.is_audited = bool(is_audited)

    @property
    def learner_id(self) -> str:
        """Alias for user_id to match Sprints domain vocabulary."""
        return self.user_id

    def calculate_letter_grade(self) -> str:
        """
        Calculate academic letter grade based on standardized assessment thresholds.

        Returns:
            str: Letter grade ('A+', 'A', 'B', 'C', 'D', 'F').
        """
        score = self.assessment_score
        if score >= 95.0:
            return "A+"
        elif score >= 90.0:
            return "A"
        elif score >= 80.0:
            return "B"
        elif score >= 70.0:
            return "C"
        elif score >= 60.0:
            return "D"
        else:
            return "F"

    def flag_for_audit(self) -> None:
        """Flag this learner for random employer partner quality review."""
        self.is_audited = True

    def display_profile(self) -> str:
        """
        Polymorphic override of display_profile() demonstrating customized
        formatting for Sprints learners.

        Returns:
            str: Rich formatted multi-line string with academic performance and audit tag.
        """
        audit_tag = " [★ QUALITY AUDIT FLAGGED]" if self.is_audited else ""
        letter_grade = self.calculate_letter_grade()

        return (
            f"=== [Learner Record: {self.learner_id}]{audit_tag} ===\n"
            f"Full Name   : {self.full_name}\n"
            f"Cohort      : {self.cohort_name}\n"
            f"Score       : {self.assessment_score:.2f}% (Grade: {letter_grade})\n"
            f"Status      : {self.enrollment_status}\n"
            f"Audit State : {'FLAGGED FOR REVIEW' if self.is_audited else 'Standard (Not Audited)'}\n"
            f"Email       : {self.email}\n"
            f"=================================================="
        )

    def get_details(self) -> Dict[str, Any]:
        """
        Polymorphic override of get_details() returning enriched learner data.

        Returns:
            Dict[str, Any]: Enriched dictionary with cohort, score, and audit fields.
        """
        details = super().get_details()
        details.update({
            "learner_id": self.learner_id,
            "cohort_name": self.cohort_name,
            "assessment_score": self.assessment_score,
            "letter_grade": self.calculate_letter_grade(),
            "enrollment_status": self.enrollment_status,
            "is_audited": self.is_audited,
        })
        return details

    def __repr__(self) -> str:
        """Developer representation of Learner."""
        return (
            f"<Learner(learner_id='{self.learner_id}', score={self.assessment_score:.2f}, "
            f"audited={self.is_audited}, status='{self.enrollment_status}')>"
        )


class Instructor(User):
    """
    Subclass representing instructors and academic mentors guiding cohorts.
    Inherits from User and overrides display_profile and get_details to demonstrate
    polymorphism.

    Attributes:
        specialization (str): Educational field of expertise (e.g., 'Data Science').
        assigned_cohorts (List[str]): List of active cohorts assigned to this instructor.
    """

    def __init__(
        self,
        instructor_id: str,
        full_name: str,
        specialization: str,
        assigned_cohorts: Optional[List[str]] = None,
        email: Optional[str] = None,
        created_at: Optional[str] = None,
    ) -> None:
        """
        Initialize an Instructor entity.

        Args:
            instructor_id: Unique instructor identifier (e.g., 'SP-I-501').
            full_name: Instructor full name.
            specialization: Technical domain (e.g., 'AI & Machine Learning').
            assigned_cohorts: Optional list of cohort names.
            email: Optional email address.
            created_at: Optional timestamp string.
        """
        super().__init__(
            user_id=instructor_id,
            full_name=full_name,
            email=email,
            role="Instructor",
            created_at=created_at,
        )
        self.specialization = str(specialization).strip()
        self.assigned_cohorts: List[str] = list(assigned_cohorts) if assigned_cohorts else []

    @property
    def instructor_id(self) -> str:
        """Alias for user_id to match Sprints domain vocabulary."""
        return self.user_id

    def assign_cohort(self, cohort_name: str) -> None:
        """
        Assign an additional cohort to this instructor.

        Args:
            cohort_name: Name of the cohort to assign.
        """
        cleaned = str(cohort_name).strip()
        if cleaned and cleaned not in self.assigned_cohorts:
            self.assigned_cohorts.append(cleaned)

    def display_profile(self) -> str:
        """
        Polymorphic override of display_profile() showcasing instructor domain
        and teaching schedule.

        Returns:
            str: Multi-line string with instructional credentials and cohort list.
        """
        cohort_list = (
            ", ".join(self.assigned_cohorts)
            if self.assigned_cohorts
            else "None Currently Assigned"
        )
        return (
            f"*** [Instructor Profile: {self.instructor_id}] ***\n"
            f"Mentor Name    : {self.full_name}\n"
            f"Specialization : {self.specialization}\n"
            f"Assigned Tracks: {cohort_list}\n"
            f"Email          : {self.email}\n"
            f"**************************************************"
        )

    def get_details(self) -> Dict[str, Any]:
        """
        Polymorphic override of get_details() returning instructor credentials.

        Returns:
            Dict[str, Any]: Enriched dictionary with specialization and assigned cohorts.
        """
        details = super().get_details()
        details.update({
            "instructor_id": self.instructor_id,
            "specialization": self.specialization,
            "assigned_cohorts": self.assigned_cohorts,
            "total_cohorts": len(self.assigned_cohorts),
        })
        return details

    def __repr__(self) -> str:
        """Developer representation of Instructor."""
        return (
            f"<Instructor(instructor_id='{self.instructor_id}', "
            f"specialization='{self.specialization}', cohorts={len(self.assigned_cohorts)})>"
        )
