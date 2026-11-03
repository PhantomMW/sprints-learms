"""
Unit Tests for LEARMS Domain Models (User, Learner, Instructor)
Demonstrates strict OOP inheritance, encapsulation, and polymorphism.
"""

import unittest
from code.models import User, Learner, Instructor


class TestDomainModels(unittest.TestCase):
    """Test suite for validating Object-Oriented models and polymorphic behavior."""

    def test_base_user_initialization_and_validation(self):
        """Verify User base class initializes properly and handles validation."""
        user = User(user_id="USR-001", full_name="Fatima Rashid", role="Director")
        self.assertEqual(user.user_id, "USR-001")
        self.assertEqual(user.full_name, "Fatima Rashid")
        self.assertEqual(user.role, "Director")
        self.assertEqual(user.email, "fatima.rashid@sprints.ai")
        self.assertTrue(user.validate())

        # Test invalid user
        invalid_user = User(user_id="", full_name="")
        self.assertFalse(invalid_user.validate())

    def test_learner_inheritance_and_polymorphism(self):
        """Verify Learner inherits from User and overrides polymorphic methods."""
        learner = Learner(
            learner_id="SP-L-1001",
            full_name="Ahmed Youssef",
            cohort_name="Data Science Cohort 5",
            assessment_score=85.50,
            enrollment_status="Active",
            is_audited=False,
        )

        # Inheritance checks
        self.assertIsInstance(learner, User)
        self.assertEqual(learner.role, "Learner")
        self.assertEqual(learner.learner_id, "SP-L-1001")
        self.assertEqual(learner.user_id, "SP-L-1001")
        self.assertIsInstance(learner.assessment_score, float)
        self.assertEqual(learner.assessment_score, 85.50)
        self.assertEqual(learner.calculate_letter_grade(), "B")

        # Polymorphic display profile
        profile = learner.display_profile()
        self.assertIn("Learner Record: SP-L-1001", profile)
        self.assertIn("Score       : 85.50% (Grade: B)", profile)
        self.assertNotIn("QUALITY AUDIT FLAGGED", profile)

        # Flag for audit
        learner.flag_for_audit()
        self.assertTrue(learner.is_audited)
        audited_profile = learner.display_profile()
        self.assertIn("[★ QUALITY AUDIT FLAGGED]", audited_profile)
        self.assertIn("Audit State : FLAGGED FOR REVIEW", audited_profile)

        # Polymorphic details dictionary
        details = learner.get_details()
        self.assertEqual(details["learner_id"], "SP-L-1001")
        self.assertEqual(details["cohort_name"], "Data Science Cohort 5")
        self.assertEqual(details["assessment_score"], 85.50)
        self.assertTrue(details["is_audited"])

    def test_instructor_inheritance_and_polymorphism(self):
        """Verify Instructor inherits from User and displays specialized profile."""
        instructor = Instructor(
            instructor_id="SP-I-501",
            full_name="Dr. Tamer Shawky",
            specialization="AI & Machine Learning",
            assigned_cohorts=["AI & Machine Learning Cohort 2"],
        )

        self.assertIsInstance(instructor, User)
        self.assertEqual(instructor.role, "Instructor")
        self.assertEqual(instructor.specialization, "AI & Machine Learning")
        self.assertIn("AI & Machine Learning Cohort 2", instructor.assigned_cohorts)

        # Assign additional cohort
        instructor.assign_cohort("Data Science Cohort 5")
        self.assertEqual(len(instructor.assigned_cohorts), 2)

        # Polymorphic display profile
        profile = instructor.display_profile()
        self.assertIn("Instructor Profile: SP-I-501", profile)
        self.assertIn("Mentor Name    : Dr. Tamer Shawky", profile)
        self.assertIn("Specialization : AI & Machine Learning", profile)
        self.assertIn("Data Science Cohort 5", profile)

    def test_score_grade_boundaries(self):
        """Verify grade categorization edge thresholds."""
        l1 = Learner("L1", "User 1", "Cohort", 96.0)
        self.assertEqual(l1.calculate_letter_grade(), "A+")
        l2 = Learner("L2", "User 2", "Cohort", 91.0)
        self.assertEqual(l2.calculate_letter_grade(), "A")
        l3 = Learner("L3", "User 3", "Cohort", 75.0)
        self.assertEqual(l3.calculate_letter_grade(), "C")
        l4 = Learner("L4", "User 4", "Cohort", 55.0)
        self.assertEqual(l4.calculate_letter_grade(), "F")

    def test_score_non_finite_and_out_of_bounds_validation(self):
        """Verify Learner constructor rejects NaN, Infinity, -Infinity, and values outside [0, 100]."""
        # Test NaN
        with self.assertRaises(ValueError):
            Learner("L-NAN", "Test User", "Cohort", float("nan"))

        # Test +Infinity
        with self.assertRaises(ValueError):
            Learner("L-INF", "Test User", "Cohort", float("inf"))

        # Test -Infinity
        with self.assertRaises(ValueError):
            Learner("L-NEGINF", "Test User", "Cohort", float("-inf"))

        # Test negative value
        with self.assertRaises(ValueError):
            Learner("L-NEG", "Test User", "Cohort", -5.0)

        # Test value > 100
        with self.assertRaises(ValueError):
            Learner("L-OVER", "Test User", "Cohort", 105.0)


if __name__ == "__main__":
    unittest.main()
