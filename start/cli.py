from re import sub
import click
import requests
from pathlib import Path
import subprocess

sources = {
    "gitignore": "https://raw.githubusercontent.com/github/gitignore/main/Python.gitignore",
    "webpack_config": "https://raw.githubusercontent.com/wagtail-examples/tutorial-deploy-pythonanywhere-paid/main/webpack.config.js",
}

def get_current_wagtail_version():
    # get the current latest wagtail version from pypi
    # using requests
    url = "https://pypi.org/pypi/wagtail/json"
    response = requests.get(url)
    data = response.json()
    return str(data["info"]["version"])


@click.command()
@click.argument("site-name")
@click.argument("wagtail-version", default=get_current_wagtail_version())
@click.option(
    "--package-name", "-p", help="The name of the package to create (e.g. webapp)"
)
def new(site_name, package_name, wagtail_version):
    """Create a new site

    Args:

        site-name (str): The name of the site directory to create (e.g. mysite)
    """

    cmd = "source $(poetry env info --path)/bin/activate && pip install wagtail=={} && deactivate".format(
        wagtail_version
    )

    subprocess.run(cmd, shell=True, check=True)

    site_name = clean_site_name(site_name)

    if not package_name:
        package_name = site_name
    else:
        package_name = package_name.lower()

    cwd = Path.cwd()  # this apps root directory
    path = cwd.parent / site_name  # the new sites root directory
    if path.exists() and path.is_dir():
        click.echo(f"Directory {path} already exists")
        return

    working_dir = path / package_name  # the new sites package directory
    working_dir.mkdir(parents=True, exist_ok=False)

    generate_site(working_dir, path, package_name, cwd)

    python_git_ignore = click.prompt(
        "Do you want to use a python gitignore? (y/n)", type=str, default="y"
    )
    if python_git_ignore == "y":
        content = subprocess.run(
            ["curl", sources.get("gitignore")], capture_output=True
        ).stdout.decode("utf-8")
        with open(path / ".gitignore", "a") as f:
            f.write(content)

    webpack = click.prompt("Do you want to use webpack? (y/n)", type=str, default="y")
    if webpack == "y":
        generate_webpack(working_dir, path, package_name, cwd)


def clean_site_name(site_name):
    """Clean the site name
    by removing spaces, dashes and dots"""
    remove_chars = ["-", ".", " "]
    for char in remove_chars:
        if char in site_name:
            site_name = site_name.replace(char, "")

    return site_name.lower()


def generate_site(working_dir, path, package_name, cwd):
    """Generate the site
    by creating the wagtail site and moving files around

    Args:
        working_dir (Path): The path to the package directory
        path (Path): The path to the site directory
        package_name (str): The name of the package
        cwd (Path): The path to this apps root directory
    """
    remove_welcome_page = click.prompt(
        "Do you want to remove the default welcome page? (y/n)", type=str, default="y"
    )
    # create the wagtail site
    subprocess.run(["wagtail", "start", package_name, str(working_dir)], check=True)

    # move the settings files
    subprocess.run(
        ["mv", str(working_dir / package_name / "settings"), str(working_dir)],
        check=True,
    )
    subprocess.run(
        ["mv", str(working_dir / package_name / "urls.py"), str(working_dir)],
        check=True,
    )
    subprocess.run(
        ["mv", str(working_dir / package_name / "wsgi.py"), str(working_dir)],
        check=True,
    )
    subprocess.run(
        ["mv", str(working_dir / package_name / "static"), str(working_dir)], check=True
    )
    subprocess.run(
        ["mv", str(working_dir / package_name / "templates"), str(working_dir)],
        check=True,
    )
    subprocess.run(
        ["mv", str(working_dir / package_name / "__init__.py"), str(working_dir)],
        check=True,
    )
    subprocess.run(["rm", "-rf", str(working_dir / package_name)], check=True)

    # move some files
    subprocess.run(["mv", str(working_dir / "manage.py"), str(path)], check=True)
    subprocess.run(["mv", str(working_dir / ".dockerignore"), str(path)], check=True)
    subprocess.run(["mv", str(working_dir / "Dockerfile"), str(path)], check=True)
    subprocess.run(["mv", str(working_dir / "requirements.txt"), str(path)], check=True)

    # alter some files
    ## URLS
    with open(cwd / "files" / "urls.py", "r") as f:
        content = f.read()
        content = content.replace("##package-name##", package_name)
    with open(working_dir / "urls.py", "w") as f:
        f.write(content)

    ## BASE
    with open(cwd / "files" / "base.py", "r") as f:
        content = f.read()
        content = content.replace("##package-name##", package_name)
    with open(working_dir / "settings/base.py", "w") as f:
        f.write(content)

    if remove_welcome_page:
        # WELCOME PAGE
        subprocess.run(
            [
                "rm",
                str(working_dir / "home" / "templates" / "home" / "welcome_page.html"),
            ],
        )

        # HOME PAGE
        with open(cwd / "files" / "home_page.html", "r") as f:
            content = f.read()
            content = content.replace("##package-name##", package_name)
        with open(
            working_dir / "home" / "templates" / "home" / "home_page.html", "w"
        ) as f:
            f.write(content)


def generate_webpack(working_dir, path, package_name, cwd):
    """Generate webpack setup
    by creating the webpack config and moving files around

    Args:
        working_dir (Path): The path to the package directory
        path (Path): The path to the site directory
        package_name (str): The name of the package
        cwd (Path): The path to this apps root directory
    """
    # GITIGNORE
    subprocess.run(["touch", ".gitignore"], cwd=path, check=True)
    with open(path / ".gitignore", "r") as f:
        content = f.read()
        content += "\n# node\nnode_modules"
    with open(path / ".gitignore", "w") as f:
        f.write(content)
    
    # NPM
    subprocess.run(["npm", "init", "-y"], cwd=path, check=True)
    subprocess.run(["touch", ".nvmrc"], cwd=path, check=True)
    with open(path / ".nvmrc", "w") as f:
        f.write("18")
    node_packages = [
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
        ["npm", "install", "--package-lock-only", *node_packages, "--save-dev"],
        cwd=path,
        check=True,
    )
    with open(path / "package.json", "r") as f:
        content = f.read()
        content = content.replace(
            '"test": "echo \\"Error: no test specified\\" && exit 1"',
            '"build": "webpack --mode production",\n    "start": "webpack --mode development --watch"',
        )
    with open(path / "package.json", "w") as f:
        f.write(content)

    # WEBPACK
    webpack_config = subprocess.run(
        ["curl", sources.get("webpack_config")], capture_output=True
    ).stdout.decode("utf-8")
    with open(path / "webpack.config.js", "w") as f:
        content = webpack_config.replace("webapp", package_name)
        f.write(content)

    # CLIENT
    subprocess.run(["mkdir", "-p", "client/scripts"], cwd=path, check=True)
    subprocess.run(["mkdir", "-p", "client/styles"], cwd=path, check=True)
    with open(path / "client/styles/index.scss", "w") as f:
        f.write("""body { background-color: #fff; color: #000; }""")
    with open(path / "client/scripts/index.js", "w") as f:
        f.write("""import "../styles/index.scss";\nconsole.log("hello world");""")

    # TEMPLATES
    with open(cwd / "files" / "base.html", "r") as f:
        content = f.read()
        content = content.replace("##package-name##", package_name)
    with open(working_dir / "templates" / "base.html", "w") as f:
        f.write(content)

    # REMOVE STATIC
    subprocess.run(
        ["rm", "-rf", str(working_dir / "home" / "static")],
    )
    subprocess.run(["rm", "-rf", str(working_dir / "static" / "css")])
    subprocess.run(["rm", "-rf", str(working_dir / "static" / "js")])
