import ejudge
from iospec import parse as parse_iospec

# Can be mocked to False during tests
SANDBOX = True


def iospec_expand(iospec: str, source: str, language: str):
    """
    Expand iospec template using a program.

    Args:
        iospec:
            A string of iospec template
        source:
            Source code for the expansion program.
        language:
            Language used in the expansion program.

    Returns:
        An expanded iospec data.
    """

    iospec_ = parse_iospec(iospec)
    results = ejudge.run(source, iospec_, lang=language, sandbox=SANDBOX)
    return results.source()


def grade_submission(iospec: str, source: str, language: str):
    """
    Grade source code from submission using the given iospec data.

    Args:
        iospec:
            A string with iospec examples used to grade the submission.
        source:
            The source code for the submission program.
        language:
            The programming language used in the submission.

    Returns:
        grade (float):
            A numeric grade between 0-100.
        feedback:
            A JSON representation with the complete feedback.
    """

    iospec_ = parse_iospec(iospec)
    results = ejudge.grade(source, iospec_, lang=language, sandbox=SANDBOX)
    grade = results.grade * 100
    return (grade, results.to_json())
