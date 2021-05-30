"""Course Plan is a collection of Semester Plans"""
import os
from dataclasses import dataclass
from typing import List, Match, Optional, Tuple, Type, TypeVar

import regex as re

from course import Course
from semesterplan import SemesterPlan

CoursePlanType = TypeVar("CoursePlanType", bound="CoursePlan")

RE_OPT = re.DOTALL


@dataclass
class CoursePlan:
    """Course Plan represents a collection of SemesterPlans"""

    name: str
    major: str

    plan: List[SemesterPlan]

    def __init__(self) -> None:
        self.name = ""
        self.major = ""
        self.plan = []

    @classmethod
    def from_text(cls: Type[CoursePlanType], transcript: str) -> CoursePlanType:
        """Make Course Plan given major & graduation info from transcript.

        Args:
            cls (Type[CoursePlanType]): class (classmethod)
            transcript (str): the string containing your entire transcript

        Raises:
            ValueError: 1 of several regex's Failed

        Returns:
            CoursePlanType: `CoursePlan`
        """
        self = cls()
        self.parse_name(transcript)
        header_match = re.search(
            r"(?<=Unofficial\ UNDERGRADUATE\ ACADEMIC\ RECORD).*?(?=---)",
            transcript,
            RE_OPT,
        )
        if not header_match:
            raise ValueError("Could not find header from input")
        header = header_match.group(0)
        self.parse_major(header)
        self.initialize_plan(transcript)
        self.fill_plan_from_transcript(transcript)
        return self

    def parse_name(self, transcript: str) -> None:
        """Parse name from transcript.py

        Args:
            transcript (str): Text containing transcript.py

        Raises:
            ValueError: Your name could not be found...
                        Is it at the top of `Transcript.txt`?
        """
        name_match = re.match(
            r".*(?=Unofficial\ UNDERGRADUATE\ ACADEMIC\ RECORD)", transcript, RE_OPT
        )
        if not name_match:
            raise ValueError("Name not found")
        self.name = name_match.group(0).strip()

    def parse_major(self, header_text: str) -> None:
        """Parse your major from header text from transcript. We assume only 1 major.txt

        Args:
            header_text (str): Text containing only the header of transcript

        Raises:
            ValueError: Regex to find major failed
        """
        major_match = re.search(r"(?<=Major:)\s*?\K.*?(?=\n)", header_text, RE_OPT)
        if not major_match:
            raise ValueError("Major not found")
        self.major = major_match.group(0).strip()

    def get_plan_str(self, transcript_text: str) -> str:
        """Get the string containing the study plan for major, year.txt

        Args:
            transcript_text (str): The text of transcript to

        Raises:
            ValueError: Regex failed to find any semesters... check input transcript
            NotImplementedError: Study Plan is specific to major, year.
                                I did not add every one I found.

        Returns:
            str: The string containing your study plan
        """
        first_sem_match = re.search(r".*?---\K\d*\s\w*(?=---)", transcript_text)
        if not first_sem_match:
            raise ValueError("Could not identify any semesters on transcript")
        first_sem = first_sem_match.group(0)
        year = first_sem.split()[0]
        if first_sem.endswith("Fall"):
            pass  # year is correct
        else:
            year = str(int(year) - 1)  # Need to use previous year's plan
        file_path = os.path.join("Study Plans", self.major, year)
        if not os.path.exists(file_path):
            raise NotImplementedError(
                "Your Major and Year have yet to be input into the system. Consider contributing."
            )
        with open(file_path) as plan_file:
            plan_str = plan_file.read()
        return plan_str

    def initialize_plan(self, transcript_s: str) -> None:
        """Initialize the plan from your study plan.

        Args:
            transcript_s (str): Your transcript, to identify which study plan you need.

        Raises:
            ValueError: Study Plan contained no terms (per regex)
        """
        plan_s = self.get_plan_str(transcript_s)

        def get_term_match(transcript_partial: str) -> Match[str]:
            match_obj: Match[str] = re.search(r".*?\KTERM\s\d+", transcript_partial)
            return match_obj

        def remove_semester(transcript_partial: str) -> str:
            transcript_partial = transcript_partial.strip()
            transcript_partial = transcript_partial[len("TERM") :]
            index = re.search("TERM", transcript_partial, re.IGNORECASE).start()
            return transcript_partial[index:]

        match_obj = get_term_match(plan_s)
        if not match_obj:
            raise ValueError("Could not find a single term in study plan")
        while match_obj:
            plan_s = plan_s[match_obj.start() :]
            semester_plan = SemesterPlan.from_studyplan_text(
                plan_s, int(match_obj.group(0).split()[-1])
            )
            self.plan.append(semester_plan)
            try:
                plan_s = remove_semester(plan_s)
            except AttributeError:
                break
            match_obj = get_term_match(plan_s)

    def fill_plan_from_transcript(self, transcript: str) -> None:
        """Update Semester Plans' Courses' fulfilled status.
            Output any extra courses to `Failed.txt`.

        Args:
            transcript (str): The string containing a transcript
        """

        def remove_bar(partial_transcript: str, is_first: bool) -> str:
            if is_first:
                match = re.search(
                    r"---.*?\n[\S\s]*?---\K\n", partial_transcript, re.DOTALL
                )
                if not match:
                    raise ValueError(
                        "Found first semester, but couldn't find header bar"
                        + "(below first semester) in transcript"
                    )
            else:
                match = re.search(r"-*\n", partial_transcript)
                if not match:
                    raise ValueError("Could not find bar to remove")
            partial_transcript = partial_transcript[match.end() :].strip()
            return partial_transcript

        def find_next_term(
            part_transcript: str, is_first: bool = False
        ) -> Tuple[Optional[str], Optional[str]]:
            match = re.search(r"---\K\w*\s\w*(?=---)", part_transcript)
            if is_first:
                if match:
                    part_transcript = part_transcript[match.end() :]
                    part_transcript = remove_bar(part_transcript, is_first)
                else:
                    raise ValueError("Could not find the first semester in transcript")
            else:
                if match:
                    part_transcript = part_transcript[match.end() :]
                    part_transcript = remove_bar(part_transcript, is_first)
                else:
                    return None, None
            return part_transcript, match.group(0)

        def isolate_term(transcript: str) -> str:
            match = re.search(r"-*?---\n", transcript)
            return transcript[: match.start()]

        is_first_term = True
        term_found = False
        courses_taken = []
        while is_first_term or not term_found:
            s_ret, sem_title_ret = find_next_term(transcript, is_first_term)
            if not s_ret:
                term_found = True
                break
            assert isinstance(s_ret, str) and isinstance(sem_title_ret, str)
            transcript, sem_title = s_ret, sem_title_ret
            term_s = isolate_term(transcript)
            if is_first_term:
                is_first_term = False
            while term_s != "":
                course_obj, term_s = Course.from_transcript(term_s, sem_title)
                courses_taken.append(course_obj)
        self.fill_plan(courses_taken)

    def fill_plan(self, course_list: List[Course]) -> None:
        """Fill plan from list of courses taken or to be taken from.

        Args:
            course_list (List[Course]): The list of courses taken (pos in future)
        """
        for transcript_course in course_list:
            for semester in self.plan:
                if not transcript_course.fulfilled:
                    for sem_course in semester.required_courses:
                        if not transcript_course.fulfilled and not sem_course.fulfilled:
                            if transcript_course == sem_course:
                                transcript_course.fulfilled = True
                                sem_course.fulfilled = True
                                sem_course.sem_taken = transcript_course.sem_taken
                                sem_course.grade = transcript_course.grade
                                sem_course.section = transcript_course.section
        course_list = [x for x in course_list if not x.fulfilled]
        course_list = sorted(course_list, key=lambda c: c.dept)
        with open("Failed.txt", "w") as fail_out:
            for transcript_course in course_list:
                fail_out.write(
                    f"{transcript_course.sem_taken}".ljust(15)
                    + f"{transcript_course.dept} {transcript_course.number}-{transcript_course.section}".ljust(
                        20
                    )
                    + f"{transcript_course.title}".ljust(50)
                    + f"{transcript_course.grade}".ljust(5)
                    + "\n"
                )

    def output_schedule(self) -> None:
        """Fill out course plan to `Output.txt`."""
        with open("Output.txt", "w") as out_file:
            for sem in self.plan:
                out_file.write(sem.title.center(15 + 20 + 50 + 5) + "\n\n")
                for course in sem.required_courses:
                    if course.special:
                        out_file.write("*" * 10 + " " * 5 + f"{course.special_type}\n")
                    elif course.grade != "":
                        out_file.write(
                            course.sem_taken.ljust(15)
                            + f"{course.dept} {course.number}-{course.section}".ljust(
                                20
                            )
                            + course.title.ljust(50)
                            + course.grade.ljust(5)
                            + "\n"
                        )
                    else:
                        out_file.write(
                            "AP/UNK".ljust(15)
                            + f"{course.dept} {course.number}-{course.section}".ljust(
                                20
                            )
                            + course.title.ljust(50)
                            + "AP/UNK".ljust(5)
                            + "\n"
                        )
                out_file.write("\n\n")
