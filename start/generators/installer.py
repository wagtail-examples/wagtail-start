import subprocess

import click
import requests


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

    def __init__(self):
        url = "https://pypi.org/pypi/wagtail/json"
        response = requests.get(url)
        data = response.json()
        self.wagtail_version = str(data["info"]["version"])

    def change_version(self, version):
        self.wagtail_version = version

    def install_wagtail(self):
        url = f"https://pypi.org/pypi/wagtail/{self.wagtail_version}/json"
        response = requests.get(url)

        if response.status_code != 200:
            return False

        click.echo(
            click.style(
                "Installing wagtail",
                fg="black",
                bg="green",
            )
        )

        try:
            subprocess.run(
                f"""source $(poetry env info --path)/bin/activate &&
                pip install wagtail=={self.wagtail_version} && deactivate""",
                shell=True,
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return True
        except subprocess.CalledProcessError as e:  # pragma: no cover
            return {"error": e.stderr.decode("utf-8")}
