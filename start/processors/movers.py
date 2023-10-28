import subprocess


def move_files_settings(working_dir, package_name, path):
    subprocess.run(  # folder
        ["mv", str(working_dir / package_name / "settings"), str(working_dir)],
        check=True,
    )
    subprocess.run(  # file
        ["mv", str(working_dir / package_name / "urls.py"), str(working_dir)],
        check=True,
    )
    subprocess.run(  # file
        ["mv", str(working_dir / package_name / "wsgi.py"), str(working_dir)],
        check=True,
    )
    subprocess.run(  # folder
        ["mv", str(working_dir / package_name / "static"), str(working_dir)], check=True
    )
    subprocess.run(  # folder
        ["mv", str(working_dir / package_name / "templates"), str(working_dir)],
        check=True,
    )
    subprocess.run(  # file
        ["mv", str(working_dir / package_name / "__init__.py"), str(working_dir)],
        check=True,
    )

    subprocess.run(
        ["rm", "-rf", str(working_dir / package_name)], check=True
    )  # cleans up the empty folder

    subprocess.run(["mv", str(working_dir / "manage.py"), str(path)], check=True)
    subprocess.run(["mv", str(working_dir / ".dockerignore"), str(path)], check=True)
    subprocess.run(["mv", str(working_dir / "Dockerfile"), str(path)], check=True)
    subprocess.run(["mv", str(working_dir / "requirements.txt"), str(path)], check=True)
