import click
import subprocess

from start.processors.movers import move_files_settings
from start.processors.settings import update_base_settings
from start.processors.settings import update_urls
from start.processors.welcome_page import remove_welcome_page
from start.processors.welcome_page import replace_home_page
from start.processors.readme import generate_readme

def generate_backend(working_dir, path, package_name, project_name, cwd):
    """Generate the site
    by creating the wagtail site and moving files around

    Args:
        working_dir (Path): The path to the package directory
        path (Path): The path to the site directory
        package_name (str): The name of the package
        cwd (Path): The path to this apps root directory
    """

    # create the wagtail site
    subprocess.run(
        ["wagtail", "start", package_name, str(working_dir)],
        check=True,
        stdout=subprocess.DEVNULL,
    )

    move_files_settings(working_dir, package_name, path)
    update_urls(package_name, working_dir)
    update_base_settings(package_name, working_dir)

    if click.prompt(
        "Do you want to remove the default welcome page? (y/n)", type=str, default="y"
    ):
        remove_welcome_page(working_dir)
        replace_home_page(working_dir, package_name, cwd)

    generate_readme(path, project_name)
