"""All methods related to courses"""
from dataclasses import dataclass
from typing import Any, List, Match, Tuple, Type, TypeVar

import regex as re

CourseType = TypeVar("CourseType", bound="Course")


@dataclass
class Course:
    """Course object contains information about enrollments in individual classes.

    Raises:
        ValueError: Arguments incorrect (generally input files)
        NotImplementedError: Changes made to code not made in all places necessary
        ValueError: Arguments incorrect (generally input files)

    Returns:
        [type]: [description]
    """

    # pylint: disable=too-many-instance-attributes

    fulfilled: bool = False

    dept: str = ""
    number: int = -1
    section: str = ""
    title: str = ""

    sem_taken: str = ""
    grade: str = ""

    special: bool = False
    special_type: str = ""

    def __init__(self) -> None:
        pass

    @classmethod
    def from_plan(cls: Type[CourseType], course_plan: str) -> CourseType:
        """Generate an object from a plan (first found).

        Args:
            cls (Type[CourseType]): class passed into classmethod
            course_plan (str): the course plan see {majors}/{entry_years} files for more information

        Raises:
            ValueError: Failed to find an attribute in course plan
            NotImplementedError: Code modified but incomplete

        Returns:
            CourseType: Course - the course object generated
        """
        self: CourseType = cls()

        def validate(match_obj: Match[str], match_desc: str) -> str:
            if not match_obj:
                raise ValueError(match_desc + " could not be identified")
            return str(match_obj.group(0).strip())

        c_params: List[str] = []
        course_plan = course_plan.strip()
        if course_plan.startswith("{"):
            self.special = True
            self.special_type = re.search(r"(?<={).*(?=})", course_plan).group(0)
            return self
        for i in range(2):
            course_plan = course_plan.strip()
            match = re.match(r"\w+", course_plan)
            if i == 0:
                ret = validate(match, "Department")
            elif i == 1:
                ret = validate(match, "Course Number")
            else:
                raise NotImplementedError("You need to define the other error messages")
            c_params.append(ret)
            course_plan = course_plan[match.end() :].strip()
        name = re.match(r"[\S\ ]*", course_plan)
        if name:
            self.title = name.group(0).strip()
        self.dept = c_params[0]
        self.number = int(c_params[1])
        return self

    @classmethod
    def from_transcript(
        cls: Type[CourseType], transcript: str, sem_str: str
    ) -> Tuple[CourseType, str]:
        """Make the next course seen in the transcript.

        Args:
            cls (Type[CourseType]): class (classmethod)
            transcript (str): The transcript, with the top chopped off...
                                ie next string is the course itself
            sem_str (str): The name of the semester ie 20F or 2020 Fall

        Returns:
            Tuple[CourseType, str]:
                1) The object generated
                2) the transcript with the course removed from the top
        """

        def get_match(reg: str, query_string: str) -> Tuple[str, str]:
            match_obj = re.match(reg, query_string)
            if not match_obj:
                raise ValueError("Failed to use regex")
            return query_string[match_obj.end() :].strip(), match_obj.group(0)

        self = cls()
        transcript, self.dept = get_match(r"\w*", transcript)
        transcript, course_number_str = get_match(r"\w*", transcript[1:])
        self.number = int(course_number_str)
        transcript, self.section = get_match(r"-\K\w+", transcript)
        transcript, self.title = get_match(r".*?(?=(\ \ )|(\n))", transcript)
        transcript, self.grade = get_match(
            r".*?(\/)?\K[\w\-+]*?(?=(\ \ )|(\n))", transcript
        )
        self.sem_taken = sem_str
        try:
            transcript = transcript[transcript.index("\n") :].strip()
        except ValueError:
            transcript = ""
        # transcript
        # Dept-code -number-section name (\n) grade points earned
        return self, transcript

    def __eq__(self, other: Any) -> bool:
        return_state: bool = False
        if isinstance(self, Course):
            if isinstance(other, Course):
                return_state = self.dept == other.dept and self.number == other.number
        return return_state
