import os
import sys

from invoke import task
from invoke.exceptions import UnexpectedExit


@task
def install(ctx):
    """
    Install dependencies and prepare server.
    """

    _run(ctx, 'Installing dependencies...',
         '%s -m pip install .[dev] -r requirements.txt' % sys.executable)

    db(ctx)
    superuser(ctx)


@task
def db(ctx, run=False):
    """
    Alias to django makemigrations + migrate commands.
    """

    _run(ctx, 'Creating migrations',
         '%s manage.py makemigrations' % sys.executable, pty=True)
    _run(ctx, 'Applying migrations',
         '%s manage.py migrate' % sys.executable, pty=True)
    if run:
        globals()['run'](ctx)


@task
def superuser(ctx):
    """
    Creates a admin (password: admin) user.
    """

    print('Creating the admin username (password: admin)', end='')
    _django()
    from django.contrib.auth.models import User

    admin = User(username='admin', email='admin@admin.com', is_active=True,
                 is_superuser=True, is_staff=True)
    admin.save()
    admin.set_password('admin')
    admin.save()
    print('  ...done!')


@task
def run(ctx):
    """
    Run test server
    """

    redis(ctx)
    celery(ctx, True)
    _run(ctx, 'Starting dev server',
         '%s manage.py runserver' % sys.executable, pty=True)


@task
def redis(ctx):
    """
    Start redis server, if necessary.
    """
    import redis

    try:
        redis.Connection().connect()
    except redis.ConnectionError:
        _run(ctx, 'Starting redis server', 'redis-server --daemonize yes')


@task
def celery(ctx, detach=False):
    """
    Starts django celery broker.
    """

    try:
        ctx.run('celery -A ejudge_server status', pty=True)
    except UnexpectedExit:
        extra = ' -D' if detach else ''
        ret = _run(ctx, 'Starting celery',
                   'celery worker -A ejudge_server -l info' + extra, pty=True)
    else:
        print('Celery already running.')


def _run(ctx, title, cmd, **kwargs):
    """
    Runs command with echo and with the given title.
    """

    print(title)
    print(cmd)
    return ctx.run(cmd, **kwargs)


def _django():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ejudge_server.settings")

    import django
    django.setup()
    return django
