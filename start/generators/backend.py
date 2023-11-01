import click
import subprocess

from start.processors.movers import move_files_settings
from start.processors.settings import update_base_settings
from start.processors.settings import update_urls
from start.processors.welcome_page import remove_welcome_page
from start.processors.welcome_page import replace_home_page
from start.processors.readme import generate_readme


def generate_backend(path_manager):
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
        [
            "wagtail",
            "start",
            path_manager.package_name,
            str(path_manager.project_path / path_manager.package_name),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
    )
    move_files_settings(path_manager)
    update_urls(path_manager)
    update_base_settings(path_manager)

    if click.prompt(
        "Do you want to remove the default welcome page? (y/n)", type=str, default="y"
    ):
        remove_welcome_page(path_manager)
        replace_home_page(path_manager)

    generate_readme(path_manager)
