import subprocess


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
