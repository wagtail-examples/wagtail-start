import re

from dataclasses import dataclass
from pathlib import Path
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
