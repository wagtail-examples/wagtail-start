def update_urls(path_manager):
    old = "from search import views as search_views"
    new = f"from {path_manager.package_name}.search import views as search_views"

    with open(path_manager.package_path / "urls.py", "r") as f:
        content = f.read()
        content = content.replace(old, new)

    with open(path_manager.package_path / "urls.py", "w") as f:
        f.write(content)


def update_base_settings(path_manager):
    with open(path_manager.package_path / "settings" / "base.py", "r") as f:
        content = f.read()
        # Double quotes used by 3.0+
        content = content.replace('"home",', f'"{path_manager.package_name}.home",')
        content = content.replace('"search",', f'"{path_manager.package_name}.search",')
        # Single quotes used up to 2.16
        content = content.replace("'home',", f"'{path_manager.package_name}.home',")
        content = content.replace("'search',", f"'{path_manager.package_name}.search',")

    with open(path_manager.package_path / "settings" / "base.py", "w") as f:
        f.write(content)
