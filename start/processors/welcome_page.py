import subprocess

def remove_welcome_page(path_manager):
    # print("Removing welcome page")
    # print(path_manager.project_path)
    # print(path_manager.package_path)
    # print(path_manager.package_name)
    # exit()
    subprocess.run(
        [
            "rm",
            str(path_manager.package_path / "home" / "templates" / "home" / "welcome_page.html"),
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
        path_manager.package_path / "home" / "templates" / "home" / "home_page.html", "w"
    ) as f:
        f.write(home_page)
