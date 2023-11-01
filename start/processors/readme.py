def generate_readme(path_manager) -> str:
    content = f"""# { path_manager.package_name }

This project was generated using [Wagtail Start CLI](https://github.com/wagtail-examples/wagtail-start)

## Development

### Wagtail

Create a virtual environment and install the dependencies from requirements.txt

In a console, at the root of the project run:

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Frontend

The frontend is built using webpack and you'll find a .nvmrc file in the root of the project.
If you have nvm installed, you can run `nvm use` to switch to the correct node version.

In a second console run:

```bash
npm install
npm start
```
"""

    with open(path_manager.project_path / "README.md", "w") as f:
        f.write(content)
