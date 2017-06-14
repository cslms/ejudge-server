import ejudge
from iospec import parse as parse_iospec


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
    results = ejudge.run(source, iospec_, lang=language)
    return results.source()