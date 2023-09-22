# Wagtail Start

A CLI tool to quickly start a new Wagtail project.

## Installation

```bash
poetry install
```

## Usage

```bash
poetry run new [project_name]
```

The project will be created in it's own directory inside the parent directory of the CLI tool.

## Options

- Remove the default welcome page
- Add node and npm to the project
- Add webpack to the project

## New site development

Once the site is generated, you can start developing it further.

### Backend

1. Install the dependencies, use your method of setting up a virtual environment.
2. Run the migrations: `python manage.py migrate`
3. Create a superuser: `python manage.py createsuperuser`
4. Run the server: `python manage.py runserver`

### Frontend

1. Install the dependencies: `nvm use` if you have nvm installed and `npm install`.
2. Run the dev server: `npm start`.
3. Open the site in your browser: `http://localhost:3000`.
4. For production build: `npm run build`.
