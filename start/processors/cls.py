import re
import requests

from dataclasses import dataclass
from pathlib import Path
from sys import version
from typing import Optional

@dataclass
class PathManager:
    project_name: str
    package_name: str
    project_path: Optional[Path] = None
    package_path: Optional[Path] = None

    def __post_init__(self):
        self.cwd = Path.cwd()
        self.project_name = self.sanitize_name(self.project_name)
        self.package_name = self.sanitize_name(self.package_name)
        self.project_path = self.cwd.parent / self.project_name
        self.package_path = self.project_path / self.package_name

    def sanitize_name(self, name):
        # Replace special characters with underscores
        name = re.sub(r'[^\w\s-]', '_', name)
        # Replace spaces, dashes, and dots with underscores
        name = re.sub(r'[\s.-]+', '_', name)
        return name
    
    def get_cwd(self):
        return Path.cwd()
    
    def path_exists(self, path):
        return path.exists() and path.is_dir()


@dataclass
class PyPiClient:
    """A client for the PyPi API
    to get the available versions of wagtail
    
    It will only include the release versions that are not pre-release versions
    """

    base_url: str = "https://pypi.org/pypi/wagtail/json"
    base_response: Optional[dict] = None
    base_versions: Optional[list] = None

    def __post_init__(self):
        resp = requests.get(self.base_url)
        self.base_response = resp.json()
        self.base_versions = self._reduce_versions(list(self.base_response["releases"].keys()))

    def _reduce_versions(self, versions):
        # remove pre-release versions
        reduced_versions = []
        for version in versions:
            if not "rc" in version and not "b" in version and not "a" in version:
                reduced_versions.append(version)

        reduced_versions = self._fix_2_digit_versions(reduced_versions)

        return reduced_versions
    
    def _fix_2_digit_versions(self, versions):
        # update 2 digit versions to 3 digit versions
        # e.g. 2.9 -> 2.9.0
        for version in versions:
            if len(version.split(".")) == 2:
                versions[versions.index(version)] = f"{version}.0"
        
        return versions
