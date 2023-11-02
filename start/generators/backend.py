import subprocess

import click

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


def move_files_settings(path_manager):
    subprocess.run(  # SETTINGS
        [
            "mv",
            str(path_manager.package_path / path_manager.package_name / "settings"),
            str(path_manager.package_path),
        ],
        check=True,
    )

    subprocess.run(  # URLS
        [
            "mv",
            str(path_manager.package_path / path_manager.package_name / "urls.py"),
            str(path_manager.package_path),
        ],
        check=True,
    )

    subprocess.run(  # WSGI
        [
            "mv",
            str(path_manager.package_path / path_manager.package_name / "wsgi.py"),
            str(path_manager.package_path),
        ],
        check=True,
    )

    subprocess.run(  # STATIC
        [
            "mv",
            str(path_manager.package_path / path_manager.package_name / "static"),
            str(path_manager.package_path),
        ],
        check=True,
    )

    subprocess.run(  # TEMPLATES
        [
            "mv",
            str(path_manager.package_path / path_manager.package_name / "templates"),
            str(path_manager.package_path),
        ],
        check=True,
    )

    subprocess.run(  # INIT
        [
            "mv",
            str(path_manager.package_path / path_manager.package_name / "__init__.py"),
            str(path_manager.package_path),
        ],
        check=True,
    )

    subprocess.run(
        ["rm", "-rf", str(path_manager.package_path / path_manager.package_name)],
        check=True,
    )  # FOLDER

    subprocess.run(
        ["mv", str(path_manager.package_path / "manage.py"), path_manager.project_path],
        check=True,
    )  # MANAGE

    subprocess.run(
        [
            "mv",
            str(path_manager.package_path / ".dockerignore"),
            path_manager.project_path,
        ],
        check=True,
    )  # DOCKERIGNORE

    subprocess.run(
        [
            "mv",
            str(path_manager.package_path / "Dockerfile"),
            path_manager.project_path,
        ],
        check=True,
    )  # DOCKERFILE

    subprocess.run(
        [
            "mv",
            str(path_manager.package_path / "requirements.txt"),
            path_manager.project_path,
        ],
        check=True,
    )  # REQUIREMENTS


def update_urls(path_manager):
    old = "from search import views as search_views"
    new = f"from {path_manager.package_name}.search import views as search_views"

    with open(path_manager.package_path / "urls.py", "r") as f:
        content = f.read()
        content = content.replace(old, new)

    with open(path_manager.package_path / "urls.py", "w") as f:
        f.write(content)


def update_base_settings(path_manager):
    with open(path_manager.package_path / "settings" / "base.py", "r") as f:
        content = f.read()
        # Double quotes used by 3.0+
        content = content.replace('"home",', f'"{path_manager.package_name}.home",')
        content = content.replace('"search",', f'"{path_manager.package_name}.search",')
        # Single quotes used up to 2.16
        content = content.replace("'home',", f"'{path_manager.package_name}.home',")
        content = content.replace("'search',", f"'{path_manager.package_name}.search',")

    with open(path_manager.package_path / "settings" / "base.py", "w") as f:
        f.write(content)
