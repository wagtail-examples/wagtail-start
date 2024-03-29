import subprocess


def generate_frontend(path_manager, ignore_append):
    """Generate webpack setup
    by creating the webpack config and moving files around

    Args:
        working_dir (Path): The path to the package directory
        path (Path): The path to the site directory
        package_name (str): The name of the package
        cwd (Path): The path to this apps root directory
    """

    # CLIENT
    subprocess.run(
        ["mkdir", "-p", "client/scripts"], cwd=path_manager.project_path, check=True
    )
    subprocess.run(
        ["mkdir", "-p", "client/styles"], cwd=path_manager.project_path, check=True
    )
    with open(
        path_manager.get_cwd() / "start" / "generators" / "files" / "index.scss", "r"
    ) as f:
        scss_content = f.read()

    with open(path_manager.project_path / "client/styles/index.scss", "w") as f:
        f.write(scss_content)
    with open(path_manager.project_path / "client/scripts/index.js", "w") as f:
        f.write("""import "../styles/index.scss";\nconsole.log("hello world");""")

    # TEMPLATES
    with open(path_manager.package_path / "templates" / "base.html", "r") as f:
        content = f.read()
        content = content.replace(
            f"'css/{path_manager.package_name}.css'",
            f"'{path_manager.package_name}/bundle.css'",
        )
        content = content.replace(
            f"'js/{path_manager.package_name}.js'",
            f"'{path_manager.package_name}/bundle.js'",
        )
    with open(path_manager.package_path / "templates" / "base.html", "w") as f:
        f.write(content)

    # REMOVE STATIC
    subprocess.run(
        ["rm", "-rf", str(path_manager.package_path / "home" / "static")],
    )
    subprocess.run(["rm", "-rf", str(path_manager.package_path / "static" / "css")])
    subprocess.run(["rm", "-rf", str(path_manager.package_path / "static" / "js")])

    # ADD CSRF_TRUSTED_ORIGINS
    with open(path_manager.package_path / "settings" / "dev.py", "r") as f:
        content = f.read()
        content = content.replace(
            'ALLOWED_HOSTS = ["*"]',
            'ALLOWED_HOSTS = ["*"]\n\nCSRF_TRUSTED_ORIGINS = ["http://localhost:3000"]',
        )
    with open(path_manager.package_path / "settings" / "dev.py", "w") as f:
        f.write(content)

    # GIT IGNORE
    append_line = "\n# node\nnode_modules\n"

    if ignore_append:
        with open(path_manager.project_path / ".gitignore", "r") as f:
            content = f.read()
            if append_line not in content:
                content += append_line
                with open(path_manager.project_path / ".gitignore", "w") as f:
                    f.write(content)
    else:
        with open(path_manager.project_path / ".gitignore", "a") as f:
            f.write(append_line)

    # NPM
    subprocess.run(
        ["npm", "init", "-y"],
        cwd=path_manager.project_path,
        capture_output=True,
    )

    with open(path_manager.project_path / ".nvmrc", "w") as f:
        f.write("18")

    dev_packages = [
        "@babel/preset-env",
        "babel-loader",
        "browser-sync-webpack-plugin",
        "css-loader",
        "mini-css-extract-plugin",
        "sass",
        "sass-loader",
        "webpack",
        "webpack-cli",
        "webpack-dev-server",
    ]
    subprocess.run(
        ["npm", "install", "--package-lock-only", *dev_packages, "--save-dev"],
        cwd=path_manager.project_path,
        capture_output=True,
    )
    with open(path_manager.project_path / "package.json", "r") as f:
        content = f.read()
        content = content.replace(
            '"test": "echo \\"Error: no test specified\\" && exit 1"',
            '"build": "webpack --mode production",\n    "start": "webpack --mode development --watch"',
        )
    with open(path_manager.project_path / "package.json", "w") as f:
        f.write(content)

    # WEBPACK CONFIG
    with open(
        path_manager.get_cwd() / "start" / "generators" / "files" / "webpack.config.js",
        "r",
    ) as f:
        webpack_content = f.read()
    with open(path_manager.project_path / "webpack.config.js", "w") as f:
        f.write(webpack_content.replace("webapp", path_manager.package_name))
