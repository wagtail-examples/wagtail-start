# Wagtail Start

A CLI tool to quickly start a new Wagtail project.

## Installation

```bash
poetry install
```

## Usage

```bash
poetry run new [project_name] [package_name] [-v|--version]
```

Arguments:

- project_name: The name of the project default is `mysite`
- package_name: The name of the package default is `app`

Options:

- -v, --version: Choose the Wagtail version, default is `latest`

The project will be created in the [project_name] inside the parent directory of the CLI tool.

## Extra Options

- Remove the default welcome page
- Add webpack to the project

## New site development

Once the site is generated, you can start developing it further.

Open the [project_name] directory in your editor of choice. The README.md file will contain the instructions for setting up the project.
