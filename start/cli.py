from re import sub
import click
from pathlib import Path
import subprocess

sources = {
    "gitignore": "https://raw.githubusercontent.com/github/gitignore/main/Python.gitignore",
    "webpack_config": "https://raw.githubusercontent.com/wagtail-examples/tutorial-deploy-pythonanywhere-paid/main/webpack.config.js",
}


@click.command()
@click.argument("site-name")
@click.option(
    "--package-name", "-p", help="The name of the package to create (e.g. webapp)"
)
def new(site_name, package_name):
    """Create a new site

    Args:

        site-name (str): The name of the site directory to create (e.g. mysite)
    """

    if not package_name:
        package_name = site_name
    else:
        package_name = package_name.lower()

    cwd = Path.cwd()
    path = cwd.parent / site_name
    if path.exists() and path.is_dir():
        click.echo(f"Directory {path} already exists")
        return

    working_dir = path / package_name
    working_dir.mkdir(parents=True, exist_ok=False)

    remove_welcome_page = click.prompt(
        "Do you want to remove the default welcome page? (y/n)", type=str, default="y"
    )

    generate_site(working_dir, path, package_name, remove_welcome_page)

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
        generate_webpack(working_dir, path, package_name)


def generate_site(working_dir, path, package_name, remove_welcome_page):
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
    with open(working_dir / "urls.py", "r") as f:
        content = f.read()
        content = content.replace(
            "from search import views as search_views",
            f"from {package_name}.search import views as search_views",
        )

    with open(working_dir / "urls.py", "w") as f:
        f.write(content)

    with open(working_dir / "settings/base.py", "r") as f:
        content = f.read()
        content = content.replace('    "home",', f'    "{package_name}.home",')
        content = content.replace('    "search",', f'    "{package_name}.search",')

    with open(working_dir / "settings/base.py", "w") as f:
        f.write(content)

    if remove_welcome_page:
        subprocess.run(
            [
                "rm",
                str(working_dir / "home" / "templates" / "home" / "welcome_page.html"),
            ],
        )
        with open(
            working_dir / "home" / "templates" / "home" / "home_page.html", "r"
        ) as f:
            content = f.read()
            content = content.replace(
                """{% block extra_css %}

{% comment %}
Delete the line below if you're just getting started and want to remove the welcome screen!
{% endcomment %}
<link rel="stylesheet" href="{% static 'css/welcome_page.css' %}">
{% endblock extra_css %}""",
                "",
            )
            content = content.replace(
                """{% comment %}
Delete the line below if you're just getting started and want to remove the welcome screen!
{% endcomment %}
{% include 'home/welcome_page.html' %}""",
                """<h1>{{ page.title }}</h1>""",
            )
        with open(
            working_dir / "home" / "templates" / "home" / "home_page.html", "w"
        ) as f:
            f.write(content)
        subprocess.run(
            [
                "rm", "-rf", 
                str(working_dir / "home" / "static"),
            ],
        )
        subprocess.run(
            [
                "rm", "-rf",
                str(working_dir / "static" / "css" ),
            ]
        )
        subprocess.run(
            [
                "rm", "-rf",
                str(working_dir / "static" / "js" ),
            ]
        )


def generate_webpack(working_dir, path, package_name):
    subprocess.run(["touch", ".gitignore"], cwd=path, check=True)
    with open(path / ".gitignore", "r") as f:
        content = f.read()
        content += "\n# node\nnode_modules"
    with open(path / ".gitignore", "w") as f:
        f.write(content)
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
    webpack_config = subprocess.run(
        ["curl", sources.get("webpack_config")], capture_output=True
    ).stdout.decode("utf-8")
    with open(path / "webpack.config.js", "w") as f:
        content = webpack_config.replace("webapp", package_name)
        f.write(content)
    subprocess.run(["mkdir", "-p", "client/scripts"], cwd=path, check=True)
    subprocess.run(["mkdir", "-p", "client/styles"], cwd=path, check=True)
    base_styles = """body { background-color: #fff; color: #000; }"""
    base_scripts = """import "../styles/index.scss";\nconsole.log("hello world");"""
    with open(path / "client/styles/index.scss", "w") as f:
        f.write(base_styles)
    with open(path / "client/scripts/index.js", "w") as f:
        f.write(base_scripts)
    with open(working_dir / "templates" / "base.html", "r") as f:
        content = f.read()
        content = content.replace(
            "css/asite.css", "asite/bundle.css"
        )
        content = content.replace(
            "js/asite.js", "asite/bundle.js"
        )
    with open(working_dir / "templates" / "base.html", "w") as f:
        f.write(content)
