"""Make a text Application for Candidacy/Study Plan"""
from courseplan import CoursePlan


def main() -> None:
    """Run the program."""
    with open("Transcript.txt") as transcript_input_file:
        transcript_text = transcript_input_file.read()
    course_plan: CoursePlan = CoursePlan.from_text(transcript_text)
    course_plan.output_schedule()


if __name__ == "__main__":
    main()
