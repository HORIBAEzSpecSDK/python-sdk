# mypy: disable-error-code="attr-defined"
"""'horiba-sdk' is a package that provides source code for the development with Horiba devices"""

__version__ = '0.2.0'  # It MUST match the version in pyproject.toml file
from importlib import metadata as importlib_metadata


def get_version() -> str:
    try:
        return importlib_metadata.version(__name__)
    except importlib_metadata.PackageNotFoundError:  # pragma: no cover
        return 'unknown'


version: str = get_version()
