from tabnanny import check
import click
import requests
import subprocess

class WagtailVersionInstaller:
    """Install the passed in version of wagtail
    or the latest version of wagtail into the poetry virtualenv.

    Args:
        wagtail_version (str): The version of wagtail to install

    Wagtail uses semantic versioning e.g. 2.9.1

    The version passed in could be any of the following formats:
    e.g. 2.9.1 -> 2.9.1
    e.g. 2 -> 2.0
    e.g. 2.9 -> 2.9

    This will ensure the latest version of wagtail is installed for the
    major and minor version if the patch version is not specified.
    """

    def __init__(self, wagtail_version=None):
        if not wagtail_version:
            url = "https://pypi.org/pypi/wagtail/json"
            response = requests.get(url)
            data = response.json()
            self.wagtail_version = str(data["info"]["version"])
        else:
            self.wagtail_version = self.complete_minimal_wagtail_version(wagtail_version)

    def complete_minimal_wagtail_version(self, version):
        parts = version.split(".")

        if len(parts) == 3:
            return version
        
        if len(parts) == 2:
            return f"{version}.0"
        
        if len(parts) == 1:
            return f"{version}.0.0"

        raise ValueError(
            "The version of wagtail is not valid. Please use a major and minor version e.g. 2.9 or 2.9.1 if you need a patch version."
        )
    
    def change_version(self, version):
        self.wagtail_version = self.complete_minimal_wagtail_version(version)

    def install_wagtail(self):
        url = f"https://pypi.org/pypi/wagtail/{self.wagtail_version}/json"
        response = requests.get(url)

        if response.status_code != 200:
            click.echo(
                click.style(
                    f"Error: Could not find wagtail v{self.wagtail_version}",
                    fg="white",
                    bg="red",
                )
            )
            exit()
        else:
            data = response.json()
            click.echo(
                click.style(
                    "Installing wagtail",
                    fg="black",
                    bg="green",
                )
            )
        cmd = f"source $(poetry env info --path)/bin/activate && pip install wagtail=={self.wagtail_version} && deactivate"
    
        try:
            subprocess.run(
                cmd,
                shell=True,
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except subprocess.CalledProcessError as e:
            click.echo(
                click.style(
                    f"Error: Could not install wagtail v{self.wagtail_version}",
                    fg="white",
                    bg="red",
                )
            )
            exit()
