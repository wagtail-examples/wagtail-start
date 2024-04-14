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
    subprocess.run(
        ["mkdir", "-p", "client/img"], cwd=path_manager.project_path, check=True
    )
    subprocess.run(
        ["mkdir", "-p", "client/svg"], cwd=path_manager.project_path, check=True
    )
    subprocess.run(
        ["mkdir", "-p", "client/copy"], cwd=path_manager.project_path, check=True
    )

    # CSS
    with open(
        path_manager.get_cwd() / "start" / "generators" / "files" / "index.scss", "r"
    ) as f:
        scss_content = f.read()

    with open(path_manager.project_path / "client/styles/index.scss", "w") as f:
        f.write(scss_content)

    # JS
    with open(path_manager.project_path / "client/scripts/index.js", "w") as f:
        f.write("""import '../../node_modules/htmx.org/dist/htmx.min.js';""")

    # TEMPLATES
    with open(path_manager.package_path / "templates" / "base.html", "r") as f:
        content = f.read()
        content = content.replace(
            f"'css/{path_manager.package_name}.css'",
            "'css/index.css'",
        )
        content = content.replace(
            f"'js/{path_manager.package_name}.js'",
            "'js/index.js'",
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
        f.write("20")

    dev_packages = [
        "@picocss/pico",
        "browser-sync",
        "chokidar-cli",
        "htmx.org",
        "imagemin-cli",
        "imagemin-mozjpeg",
        "imagemin-pngcrush",
        "imagemin-pngquant",
        "imagemin-zopfli",
        "npm-run-all",
        "recursive-fs",
        "rollup",
        "rollup-plugin-terser",
        "sass",
        "svgo",
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
            f"""
            "clean": "recursive-delete '{path_manager.package_name}/static'",
            "js": "rollup --config",
            "css": "node sass.js",
            "svg": "svgo -f client/svg app/static/svg -r",
            "img": "imagemin client/img/* --out-dir={path_manager.package_name}/static/img --plugin=pngquant --plugin=mozjpeg --plugin=pngcrush --plugin=zopfli",
            "copy": "recursive-copy 'client/copy' '{path_manager.package_name}/static'",
            "build-dirty": "npm-run-all -p js css svg img copy",
            "build": "npm-run-all -s clean build-dirty",
            "watch-css": "chokidar './client/**/*.scss' -c 'npm run css'",
            "watch-js": "chokidar './client/**/*.js' -c 'npm run js'",
            "watch-svg": "chokidar './client/**/*.svg' -c 'npm run svg'",
            "watch-img": "chokidar './client/img/**/*.*' -c 'npm run img'",
            "watch-copy": "chokidar './client/copy/**/*.*' -c 'npm run copy'",
            "watch": "npm-run-all -p build watch-css watch-js watch-svg watch-img watch-copy",
            "server-start": "browser-sync start --proxy '127.0.0.1:8000' --files '{path_manager.package_name}/**/*/*'",
            "server": "npm-run-all -p watch server-start"
            """,  # noqa
        )
    with open(path_manager.project_path / "package.json", "w") as f:
        f.write(content)

    # ROLLUP CONFIG
    with open(
        path_manager.get_cwd() / "start" / "generators" / "files" / "rollup.config.js",
        "r",
    ) as f:
        rollup_content = f.read()
    with open(path_manager.project_path / "rollup.config.js", "w") as f:
        f.write(rollup_content.replace("webapp", path_manager.package_name))

    # SASS CONFIG
    with open(
        path_manager.get_cwd() / "start" / "generators" / "files" / "sass.js", "r"
    ) as f:
        sass_content = f.read()
    with open(path_manager.project_path / "sass.js", "w") as f:
        f.write(sass_content.replace("webapp", path_manager.package_name))

    # SVG CONFIG
    with open(
        path_manager.get_cwd() / "start" / "generators" / "files" / "svgo.config.mjs",
        "r",
    ) as f:
        svgo_content = f.read()
    with open(path_manager.project_path / "svgo.config.mjs", "w") as f:
        f.write(svgo_content)

    # MOCK SVG
    with open(
        path_manager.get_cwd() / "start" / "generators" / "files" / "mock.svg", "r"
    ) as f:
        mock_svg = f.read()
    with open(path_manager.project_path / "client/svg/mock.svg", "w") as f:
        f.write(mock_svg)
