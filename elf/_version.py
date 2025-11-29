from __future__ import annotations

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as pkg_version


def _package_name() -> str:
    """Return the root package name for metadata lookup."""
    return (__package__ or __name__).split(".")[0]


def get_package_version() -> str:
    """Return the installed package version, falling back for local development."""
    try:
        return pkg_version(_package_name())
    except PackageNotFoundError:
        return "0.0.0+local"
