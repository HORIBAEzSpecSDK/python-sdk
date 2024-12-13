# mypy: disable-error-code="attr-defined"
"""'horiba-sdk' is a package that provides source code for the development with Horiba devices"""

from loguru import logger

__version__ = '0.2.0'  # It MUST match the version in pyproject.toml file
from importlib import metadata as importlib_metadata


def get_version() -> str:
    try:
        return importlib_metadata.version(__name__)
    except importlib_metadata.PackageNotFoundError:  # pragma: no cover
        return 'unknown'


version: str = get_version()

# it is good practice to disable the logging for a library, this is done here.
# on initialization of a device manager, this can be enabled.
logger.disable(__name__)
