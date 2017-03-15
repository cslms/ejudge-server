import pytest
import ejudge_server


def test_project_defines_author_and_version():
    assert hasattr(ejudge_server, '__author__')
    assert hasattr(ejudge_server, '__version__')
