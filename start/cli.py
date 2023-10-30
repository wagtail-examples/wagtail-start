import click
import subprocess

from .functions import clean_site_name
from .functions import clean_site_name
from .functions import get_current_wagtail_version
from .functions import install_wagtail_in_virtualenv

from .generators.backend import generate_backend
from .generators.frontend import generate_frontend
from .generators.installer import WagtailVersionInstaller

from .processors.cls import PathManager, PyPiClient

sources = {
    "gitignore": "https://raw.githubusercontent.com/github/gitignore/main/Python.gitignore",
    "webpack_config": "https://raw.githubusercontent.com/wagtail-examples/tutorial-deploy-pythonanywhere-paid/main/webpack.config.js",
}


@click.command()
@click.argument("project-name", type=str, default="my_site")
@click.argument("package-name", type=str, default="webapp")
# @click.option(
#     "--version",
#     "-v",
#     type=str,
#     default=None,
#     help=f"The version of wagtail to use (e.g. 2.9 will install the latest version of wagtail 2.9.x)",
# )
def new(project_name, package_name):
    """Create a new wagtail site

    CMD: new <project_name> <package_name>

    The default <project_name> is my_site, the default <package_name> is webapp
    """

    pypi_client = PyPiClient()
    base_versions = pypi_client.base_versions

    version_installer = WagtailVersionInstaller()
    wagtail_version = version_installer.wagtail_version

    click.echo(
        click.style(f"Using wagtail v{wagtail_version}", fg="white", bg="blue"),
    )
    click.echo("Press enter to install the latest version of wagtail")

    version = click.prompt(
        "or enter a version to install? (e.g. 2.9 will install the latest version of wagtail 2.9.x)",
        type=str,
        default=wagtail_version,
    )
    
    if version_installer.complete_minimal_wagtail_version(version) not in base_versions:
        click.echo(
            click.style(
                f"Error: Could not find wagtail v{version}",
                fg="white",
                bg="red",
            )
        )
        exit()

    version_installer.change_version(version_installer.complete_minimal_wagtail_version(version))
    click.echo(
        click.style(f"Using wagtail v{version_installer.wagtail_version}.x", fg="white", bg="blue"),
    )

    click.echo("Installing wagtail, please wait...")
    version_installer.install_wagtail()

    exit()

    path_manager = PathManager(project_name=project_name, package_name=package_name)

    if path_manager.path_exists(path_manager.project_path):
        click.echo(f"Directory {path_manager.project_path} already exists")
        return

    click.echo(f"Creating new wagtail site version {wagtail_version}...")
    version_installer.install_wagtail()

    # cmd = "source $(poetry env info --path)/bin/activate && pip install wagtail=={} && deactivate".format(
    #     wagtail_version
    # )

    # install_wagtail_in_virtualenv(cmd)
    exit()

    pm.project_path.mkdir(parents=True, exist_ok=False)
    # working_dir = path / package_name  # the new sites package directory

    generate_backend(pm.project_path, package_name, project_name, cwd)

    ignore_append = False
    python_git_ignore = click.prompt(
        "Do you want to use a python gitignore? (y/n)", type=str, default="y"
    )

    if python_git_ignore == "y":
        ignore_append = True
        python_git_ignore_content = subprocess.run(
            ["curl", sources.get("gitignore")], capture_output=True
        ).stdout.decode("utf-8")
        with open(path / ".gitignore", "a") as f:
            f.write(python_git_ignore_content)

    webpack = click.prompt("Do you want to use webpack? (y/n)", type=str, default="y")
    if webpack == "y":
        generate_frontend(working_dir, path, package_name, cwd, ignore_append)
