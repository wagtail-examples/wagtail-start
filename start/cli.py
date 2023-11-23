import subprocess

import click

from .generators.backend import generate_backend
from .generators.frontend import generate_frontend
from .generators.installer import WagtailVersionInstaller
from .managers import PathManager, PyPiClient

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

    installer = WagtailVersionInstaller()
    installer_version = installer.wagtail_version

    click.echo(
        click.style(
            f"Using wagtail v{installer_version}",
            fg="yellow",
        ),
    )

    version = click.prompt(
        "Type a specific version of wagtail (e.g. 3.0.1) or press enter to continue",
        type=str,
        default=installer_version,
    )

    installer.change_version(version)

    result = installer.install_wagtail()

    if not result:
        click.echo(
            click.style(
                f"Error: Could not find wagtail v{version}",
                fg="red",
            )
        )
        click.echo(
            click.style(
                "You can run `poetry run inspect` to see all available versions",
                fg="white",
            )
        )
        return
    elif result is None:
        click.echo(
            click.style(
                f"Error: Could not install wagtail v{version} {result['error']}",
                fg="white",
                bg="red",
            )
        )

    pm = PathManager(project_name=project_name, package_name=package_name)

    if pm.path_exists(pm.project_path):
        click.echo(f"Directory {pm.project_path} already exists")
        return

    pm.create_project_path()

    click.echo("Creating new wagtail site")
    click.echo("==========================")

    generate_backend(pm)

    ignore_append = False
    python_git_ignore = click.prompt(
        "Do you want to use a python gitignore? (y/n)", type=str, default="y"
    )

    if python_git_ignore == "y":
        ignore_append = True
        python_git_ignore_content = subprocess.run(
            [
                "curl",
                "https://raw.githubusercontent.com/github/gitignore/main/Python.gitignore",
            ],
            capture_output=True,
        ).stdout.decode("utf-8")
        with open(pm.project_path / ".gitignore", "a") as f:
            f.write(python_git_ignore_content)

    webpack = click.prompt("Do you want to use webpack? (y/n)", type=str, default="y")

    if webpack == "y":
        generate_frontend(pm, ignore_append)


@click.command()
@click.argument("major", type=int, default=0)
def versions(major) -> None:
    """List available wagtail versions

    CMD: versions <major>

    The default <major> is 0, which will list all available versions
    """

    pypi_client = PyPiClient()
    base_versions = pypi_client.base_versions
    # print(base_versions)

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
    # print(result)

    # Sort the groups by the first digit
    result.sort(key=lambda x: int(x[0].split(".")[0]))
    result.reverse()

    click.echo("Available wagtail release versions:")
    click.echo("===================================")

    for group in result:
        click.echo(f"{group[0].split('.')[0]}.x: [{', '.join(group)}]")
