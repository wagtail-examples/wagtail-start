def update_urls(package_name, working_dir):
    old = "from search import views as search_views"
    new = f"from {package_name}.search import views as search_views"

    with open(working_dir / "urls.py", "r") as f:
        content = f.read()
        content = content.replace(old, new)


    with open(working_dir / "urls.py", "w") as f:
        f.write(content)

def update_base_settings(package_name, working_dir):
    with open(working_dir / "settings" / "base.py", "r") as f:
        content = f.read()
        content = content.replace('"home",', f'"{package_name}.home",')
        content = content.replace('"search",', f'"{package_name}.search",')

    with open(working_dir / "settings" / "base.py", "w") as f:
        f.write(content)
