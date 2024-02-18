# Documentation for {{app}}

This project was generated using [Wagtail Start CLI](https://github.com/wagtail-examples/wagtail-start)

## Development

### Wagtail

Create a virtual environment and install the dependencies from requirements.txt

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

In a console, at the root of the project run:

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
