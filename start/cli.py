import subprocess

import click

from .generators.backend import generate_backend
from .generators.frontend import generate_frontend
from .generators.installer import WagtailVersionInstaller
from .processors.cls import PathManager, PyPiClient

sources = {
    "gitignore": "https://raw.githubusercontent.com/github/gitignore/main/Python.gitignore",
}


@click.command()
@click.argument("project-name", type=str, default="wagtail_site")
@click.argument("package-name", type=str, default="app")
def new(project_name: str, package_name: str) -> None:
    """Create a new wagtail site

    CMD: new <project_name> <package_name>

    The default <project_name> is wagtail_site, the default <package_name> is app
    """

    pypi_client = PyPiClient()
    base_versions = pypi_client.base_versions

    version_installer = WagtailVersionInstaller()
    wagtail_version = version_installer.wagtail_version

    click.echo(
        click.style(
            f"Using wagtail v{wagtail_version}",
            fg="yellow",
        ),
    )

    version = click.prompt(
        "Type a specific version of wagtail (e.g. 3.0.1) or press enter to continue",
        type=str,
        default=wagtail_version,
    )

    if version_installer.complete_minimal_wagtail_version(version) not in base_versions:
        click.echo(
            click.style(
                f"Error: Could not find wagtail v{version}",
                fg="red",
            )
        )
        exit()

    version_installer.change_version(
        version_installer.complete_minimal_wagtail_version(version)
    )

    version_installer.install_wagtail()

    path_manager = PathManager(project_name=project_name, package_name=package_name)

    if path_manager.path_exists(path_manager.project_path):
        click.echo(f"Directory {path_manager.project_path} already exists")
        return

    path_manager.create_project_path()

    click.echo("Creating new wagtail site")
    click.echo("==========================")

    generate_backend(path_manager)

    ignore_append = False
    python_git_ignore = click.prompt(
        "Do you want to use a python gitignore? (y/n)", type=str, default="y"
    )

    if python_git_ignore == "y":
        ignore_append = True
        python_git_ignore_content = subprocess.run(
            ["curl", sources.get("gitignore")], capture_output=True
        ).stdout.decode("utf-8")
        with open(path_manager.project_path / ".gitignore", "a") as f:
            f.write(python_git_ignore_content)

    webpack = click.prompt("Do you want to use webpack? (y/n)", type=str, default="y")

    if webpack == "y":
        generate_frontend(path_manager, ignore_append)


@click.command()
@click.argument("major", type=int, default=0)
def versions(major) -> None:
    """List available wagtail versions

    CMD: versions <major>

    The default <major> is 0, which will list all available versions
    """

    pypi_client = PyPiClient()
    base_versions = pypi_client.base_versions

    grouped_data = {}
    for item in base_versions:
        first_digit = item.split(".")[0]
        if major != 0 and int(first_digit) != major:
            continue
        if first_digit in grouped_data:
            grouped_data[first_digit].append(item)
        else:
            grouped_data[first_digit] = [item]

    result = list(grouped_data.values())

    # Sort the groups by the first digit
    result.sort(key=lambda x: int(x[0].split(".")[0]))
    result.reverse()

    click.echo("Available wagtail release versions:")
    click.echo("===================================")

    for group in result:
        click.echo(f"{group[0].split('.')[0]}.x: [{', '.join(group)}]")
