"""Semester Plan - A subdivision of a Study Plan"""
from dataclasses import dataclass, field
from typing import List, Type, TypeVar

from course import Course

SemesterPlanType = TypeVar("SemesterPlanType", bound="SemesterPlan")


@dataclass
class SemesterPlan:
    """A semester plan representing 1 semester of a studyplan."""

    title: str = ""
    number: int = -1
    required_courses: List[Course] = field(default_factory=lambda: [])

    @classmethod
    def from_studyplan_text(
        cls: Type[SemesterPlanType], study_plan: str, sem_number: int
    ) -> SemesterPlanType:
        """Generate 1 semester's study plan from the study plan provided.
            The current term should not have TERM header.

        Args:
            cls (Type[SemesterPlanType]): class (classmethod)
            study_plan (str): The study plan with the top chopped off (only takes the first term it finds)
            sem_number (int): The number refering to the semester

        Returns:
            SemesterPlanType: `SemesterPlan`
        """
        sem_plan = cls()
        sem_plan.title = study_plan[: study_plan.index("\n")].strip()
        sem_plan.number = sem_number
        study_plan = "\n".join(study_plan.split("\n")[1:])
        if "TERM" in study_plan:
            study_plan = study_plan[: study_plan.index("TERM")]
        courses = study_plan.split("\n")
        for course in courses:
            if course.strip() != "":
                sem_plan.required_courses.append(Course.from_plan(course))
        return sem_plan
