import codecs
import os

from setuptools import setup, find_packages

# Save version and author to __meta__.py
version = open('VERSION').read().strip()
dirname = os.path.dirname(__file__)
path = os.path.join(dirname, 'src', 'ejudge_server', '__meta__.py')
meta = '''# Automatically created. Please do not edit.
__version__ = '%s'
__author__ = 'F\\xe1bio Mendes'
''' % version
with open(path, 'w') as F:
    F.write(meta)

setup(
    # Basic info
    name='ejudge-server',
    version=version,
    author='Fábio Mendes',
    author_email='fabiomacedomendes@gmail.com',
    url='',
    description='A short description for your project.',
    long_description=codecs.open('README.rst', 'rb', 'utf8').read(),

    # Classifiers (see https://pypi.python.org/pypi?%3Aaction=list_classifiers)
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries',
    ],

    # Packages and dependencies
    package_dir={'': 'src'},
    packages=find_packages('src'),
    install_requires=[
        # Generic deps
        'coreapi',
        'ejudge',
        'iospec',
        'celery',
        'redis',

        # Django deps
        'django-jsonfield',
        'django==1.10',
        'djangorestframework',
        'django-celery-results',
        'django-celery-beat',
        'fake-factory==0.7.4',
    ],
    extras_require={
        'dev': [
            'python-boilerplate[dev]',
            'pytest-django',
            'pytest-cov',
            'manuel',
        ],
    },

    # Other configurations
    zip_safe=False,
    platforms='any',
)
