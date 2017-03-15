import os
import argparse

from ejudge_server import __version__


def get_parser():
    """
    Creates a new argument parser.
    """
    parser = argparse.ArgumentParser('ejudge-server')
    version = '%(prog)s ' + __version__
    parser.add_argument('--version', '-v', action='version', version=version)
    return parser


def main(args=None):
    """
    Called with ``python -m ejudge_server.tests``: run main test suite.
    """

    parser = get_parser()
    args = parser.parse_args(args)

    # Check if pytest is available
    try:
        import pytest
    except ImportError:
        raise SystemExit(
            'You need py.test to run the test suite.\n'
            'You can install it using your distribution package manager or\n'
            '    $ python -m pip install pytest --user'
        )

    # Get data from test_module
    import ejudge_server.tests as test_module
    test_path = os.path.abspath(os.path.dirname(test_module.__file__))
    pytest.main([test_path, '-m', 'not documentation'])


if __name__ == '__main__':
    main()