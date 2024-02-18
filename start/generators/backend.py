import subprocess

import click


def generate_backend(path_manager, webpack):
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

    generate_readme(path_manager, webpack)


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
    with open(
        path_manager.get_cwd() / "start" / "generators" / "files" / "home_page.html",
    ) as f:
        home_page = f.read()

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


def generate_readme(path_manager, webpack):
    with open(
        path_manager.get_cwd() / "start" / "generators" / "files" / "README.md", "r"
    ) as f:
        readme_content = f.read()
        readme_content.replace("{{app}}", path_manager.package_name)
    if webpack == "y":
        with open(
            path_manager.get_cwd() / "start" / "generators" / "files" / "README_fe.md",
        ) as f:
            readme_content += f.read()

    with open(path_manager.project_path / "README.md", "w") as f:
        f.write(readme_content)


def generate_pre_commit_config(path_manager):
    config = """repos:
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8"""

    with open(path_manager.project_path / ".pre-commit-config.yaml", "w") as f:
        f.write(config)

    isort_config = """[settings]\nprofile = black"""

    with open(path_manager.project_path / ".isort.cfg", "w") as f:
        f.write(isort_config)

    flake8_config = """[flake8]\nmax-line-length = 120"""

    with open(path_manager.project_path / ".flake8", "w") as f:
        f.write(flake8_config)

    # black has no config file


def generate_python_git_ignore(path_manager, ignore_append):
    python_git_ignore_content = subprocess.run(
        [
            "curl",
            "https://raw.githubusercontent.com/github/gitignore/main/Python.gitignore",
        ],
        capture_output=True,
    ).stdout.decode("utf-8")
    python_git_ignore_content += "\n/media\n"
    python_git_ignore_content += "\n/static\n"

    if ignore_append:
        with open(path_manager.project_path / ".gitignore", "a") as f:
            f.write(python_git_ignore_content)
    else:
        with open(path_manager.project_path / ".gitignore", "w") as f:
            f.write(python_git_ignore_content)
