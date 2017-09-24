import os
from setuptools import setup, find_packages


here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.md')) as f:
    CHANGES = f.read()

VERSION = '0.0'

requires = [
    'bcrypt',
    'cornice',
    'marshmallow',
    'marshmallow_sqlalchemy',
    'openpyxl',
    'psycopg2',
    'python-dateutil',
    'pyramid',
    'pyramid_jinja2',
    'pyramid_jwt',
    'pyramid_tm',
    'pyramid_multiauth',
    'SQLAlchemy',
    'transaction',
    'zope.sqlalchemy',
    'webargs',
    'waitress',

    # deps not on pypi
    'elixr.base',
    'elixr.sax'
]

tests_require = [
    # dev
    'pyramid_debugtoolbar',

    # tests
    'WebTest >= 1.3.1',  # py3 compat
    'pytest',            # includes virtualenv
    'pytest-cov',
]

setup(
    name='gridix',
    version=VERSION,
    description='GridIX Web',
    long_description=README + '\n\n' + CHANGES,
    classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],
    author='Abdul-Hakeem Shaibu',
    author_email='s.abdulhakeem@hotmail.com',
    url='',
    keywords='gridix',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    extras_require={
        'testing': tests_require,
    },
    install_requires=requires,
    entry_points="""\
    [paste.app_factory]
    main = gridix.webapp:main
    [console_scripts]
    initialize_gridix_db = gridix.scripts.initializedb:main
    import_gridix_data = gridix.scripts.importdt:main
    """
)
