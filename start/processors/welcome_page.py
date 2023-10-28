import subprocess

def remove_welcome_page(working_dir):
    subprocess.run(
        [
            "rm",
            str(working_dir / "home" / "templates" / "home" / "welcome_page.html"),
        ],
    )


def replace_home_page(working_dir, package_name, cwd):
    home_page = """
    {% extends "base.html" %}

    {% block body_class %}template-homepage{% endblock %}

    {% block content %}

    <h1>{{ page.title }}</h1>

    {% endblock content %}"""
    
    with open(
        working_dir / "home" / "templates" / "home" / "home_page.html", "w"
    ) as f:
        f.write(home_page)
