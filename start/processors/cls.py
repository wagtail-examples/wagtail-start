import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import requests


@dataclass
class PathManager:
    """
    Create and store paths for the project and package

    Attributes:
        project_name: The name of the project
        package_name: The name of the package
        project_path: The path to the project
        package_path: The path to the package

    Returns: None (stores paths as attributes)
    """

    project_name: str
    package_name: str
    project_path: Optional[Path] = None
    package_path: Optional[Path] = None

    def __post_init__(self):
        self.cwd = Path.cwd().parent
        self.project_name = self.sanitize_name(self.project_name)
        self.package_name = self.sanitize_name(self.package_name)
        self.project_path = self.cwd / self.project_name
        self.package_path = self.project_path / self.package_name

    def sanitize_name(self, name):
        # Replace special characters with underscores
        name = re.sub(r"[^\w\s-]", "_", name)
        # Replace spaces, dashes, and dots with underscores
        name = re.sub(r"[\s.-]+", "_", name)
        return name

    def get_cwd(self):
        return Path.cwd()

    def path_exists(self, path):
        return path.exists() and path.is_dir()

    def create_project_path(self):
        # self.project_path.mkdir(parents=True, exist_ok=False)
        self.package_path.mkdir(parents=True, exist_ok=False)


@dataclass
class PyPiClient:
    """
    A client for the PyPi API

    Gets all the available versions of wagtail.

    Attributes:
        base_url: The base url for the PyPi API
        base_response: The response from the PyPi API
        base_versions: A list of all the available versions of wagtail that aren't pre-release versions
    """

    base_url: str = "https://pypi.org/pypi/wagtail/json"
    base_response: Optional[dict] = None
    base_versions: Optional[list] = None

    def __post_init__(self) -> None:
        resp = requests.get(self.base_url)
        self.base_response = resp.json()
        self.base_versions = self._reduce_versions(
            list(self.base_response["releases"].keys())
        )

    def _reduce_versions(self, versions: list) -> list:
        reduced_versions = []
        for version in versions:
            if "rc" not in version and "b" not in version and "a" not in version:
                # remove pre-release versions
                reduced_versions.append(version)

        return reduced_versions

    def _append_2_digit_versions(self, versions: list) -> list:
        # e.g. 2.9 -> 2.9.0
        for version in versions:
            if len(version.split(".")) == 2:
                versions[versions.index(version)] = f"{version}.0"

        return versions
