import click
import requests
from pathlib import Path
import subprocess

from .generators.readme import generate_readme
from .generators.welcome_page import remove_welcome_page, replace_home_page
from .generators.settings import update_urls, update_base_settings
from .functions import clean_site_name, get_current_wagtail_version, install_wagtail_in_virtualenv

sources = {
    "gitignore": "https://raw.githubusercontent.com/github/gitignore/main/Python.gitignore",
    "webpack_config": "https://raw.githubusercontent.com/wagtail-examples/tutorial-deploy-pythonanywhere-paid/main/webpack.config.js",
}


@click.command()
@click.argument("project-name", type=str, default="my_site")
@click.argument("package-name", type=str, default="webapp")
@click.option(
    "--version",
    "-v",
    type=str,
    default=None,
    help=f"The version of wagtail to use (e.g. {get_current_wagtail_version()})",
)
def new(project_name, package_name, version):
    """Create a new wagtail site

    CMD: new <project_name> <package_name>

    The default <project_name> is my_site, the default <package_name> is webapp
    """

    project_name = clean_site_name(project_name)  # needs more work
    package_name = project_name if not package_name else package_name.lower()

    cwd = Path.cwd()  # this apps root directory
    path = cwd.parent / project_name  # the new sites root directory
    
    if path.exists() and path.is_dir():
        click.echo(f"Directory {path} already exists")
        return # exit with a message

    if not version:
        wagtail_version = click.prompt(
            "What version of wagtail do you want to use?",
            type=str,
            default=get_current_wagtail_version(),
        )

        cmd = "source $(poetry env info --path)/bin/activate && pip install wagtail=={} && deactivate".format(
            wagtail_version
        )

    click.echo(f"Creating new wagtail site version {wagtail_version}...")
    install_wagtail_in_virtualenv(cmd)

    working_dir = path / package_name  # the new sites package directory
    working_dir.mkdir(parents=True, exist_ok=False)

    generate_site(working_dir, path, package_name, project_name, cwd)

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


def generate_site(working_dir, path, package_name, project_name, cwd):
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

    update_urls(package_name, working_dir)
    update_base_settings(package_name, working_dir)

    if click.prompt(
        "Do you want to remove the default welcome page? (y/n)", type=str, default="y"
    ):
        remove_welcome_page(working_dir)
        replace_home_page(working_dir, package_name, cwd)

    generate_readme(path, project_name)


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
    subprocess.run(
        ["npm", "init", "-y"], cwd=path, check=True, stdout=subprocess.DEVNULL
    )
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
        stdout=subprocess.DEVNULL,
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
    with open(cwd / "files" / "webpack.js", "r") as f:
        content = f.read()
        content = content.replace("webapp", package_name)
    with open(path / "webpack.config.js", "w") as f:
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
