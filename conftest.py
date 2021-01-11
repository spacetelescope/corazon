try:
    from pytest_astropy_header.display import (PYTEST_HEADER_MODULES,
                                               TESTED_VERSIONS)
except ImportError:
    PYTEST_HEADER_MODULES = {}
    TESTED_VERSIONS = {}

try:
    from corazon import __version__ as version
except ImportError:
    version = 'unknown'

# The following line treats all DeprecationWarnings as exceptions.
from astropy.tests.helper import enable_deprecations_as_exceptions
enable_deprecations_as_exceptions()

# Uncomment and customize the following lines to add/remove entries
# from the list of packages for which version numbers are displayed
# when running the tests.
PYTEST_HEADER_MODULES['astropy'] = 'astropy'
PYTEST_HEADER_MODULES.pop('Pandas', None)
PYTEST_HEADER_MODULES.pop('h5py', None)

TESTED_VERSIONS['corazon'] = version
