import click
from pathlib import Path
import subprocess

from .functions import clean_site_name
from .functions import clean_site_name
from .functions import get_current_wagtail_version
from .functions import install_wagtail_in_virtualenv

from .generators.backend import generate_backend
from .generators.frontend import generate_frontend

sources = {
    "gitignore": "https://raw.githubusercontent.com/github/gitignore/main/Python.gitignore",
    "webpack_config": "https://raw.githubusercontent.com/wagtail-examples/tutorial-deploy-pythonanywhere-paid/main/webpack.config.js",
}


@click.command()
@click.argument("project-name", type=str, default="my_site")
@click.argument("package-name", type=str, default="webapp")
@click.option(
    "--version",
    "-v",
    type=str,
    default=None,
    help=f"The version of wagtail to use (e.g. {get_current_wagtail_version()})",
)
def new(project_name, package_name, version):
    """Create a new wagtail site

    CMD: new <project_name> <package_name>

    The default <project_name> is my_site, the default <package_name> is webapp
    """

    project_name = clean_site_name(project_name)  # needs more work
    package_name = project_name if not package_name else package_name.lower()

    cwd = Path.cwd()  # this apps root directory
    path = cwd.parent / project_name  # the new sites root directory

    if path.exists() and path.is_dir():
        click.echo(f"Directory {path} already exists")
        return  # exit with a message

    if not version:
        wagtail_version = click.prompt(
            "What version of wagtail do you want to use?",
            type=str,
            default=get_current_wagtail_version(),
        )

        cmd = "source $(poetry env info --path)/bin/activate && pip install wagtail=={} && deactivate".format(
            wagtail_version
        )

    click.echo(f"Creating new wagtail site version {wagtail_version}...")
    install_wagtail_in_virtualenv(cmd)

    working_dir = path / package_name  # the new sites package directory
    working_dir.mkdir(parents=True, exist_ok=False)

    generate_backend(working_dir, path, package_name, project_name, cwd)

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

