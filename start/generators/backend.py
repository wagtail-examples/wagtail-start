import subprocess

import click

from start.processors.movers import move_files_settings
from start.processors.readme import generate_readme
from start.processors.settings import update_base_settings, update_urls


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

    remove_welcome = click.prompt(
        "Do you want to remove the default welcome page? (y/n)", type=str, default="y"
    )
    if remove_welcome == "y":
        remove_welcome_page(path_manager)
        replace_home_page(path_manager)

    generate_readme(path_manager)


def remove_welcome_page(path_manager):
    subprocess.run(
        [
            "rm",
            str(
                path_manager.package_path
                / "home"
                / "templates"
                / "home"
                / "welcome_page.html"
            ),
        ],
    )


def replace_home_page(path_manager):
    home_page = """
    {% extends "base.html" %}

    {% block body_class %}template-homepage{% endblock %}

    {% block content %}

    <h1>{{ page.title }}</h1>

    {% endblock content %}"""

    with open(
        path_manager.package_path / "home" / "templates" / "home" / "home_page.html",
        "w",
    ) as f:
        f.write(home_page)
