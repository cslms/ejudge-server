import ejudge_server
from ejudge_server.utils import full_url


def test_project_defines_author_and_version():
    assert hasattr(ejudge_server, '__author__')
    assert hasattr(ejudge_server, '__version__')


class TestUtils:

    def test_full_url(self):
        assert full_url('foo', 'bar') == 'http://localhost:8000/foo/bar'
        assert full_url('foo/', 'bar') == 'http://localhost:8000/foo/bar'
        assert full_url('foo/', '/bar') == 'http://localhost:8000/foo/bar'
        assert full_url('foo', '/bar') == 'http://localhost:8000/foo/bar'
