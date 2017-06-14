from functools import reduce


def hostname():
    """
    Return the hostname of currently running instance.
    """

    return 'http://localhost:8000'


def full_url(url, *args):
    """
    Prepend url with the current hostname.
    """

    def join_path(x, y):
        if x.endswith('/') and y.startswith('/'):
            return x[:-1] + y
        elif x.endswith('/') or y.startswith('/'):
            return x + y
        else:
            return '%s/%s' % (x, y)

    path = (hostname(), url) + args
    return reduce(join_path, path)
