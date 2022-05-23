# About

`flask-createproject` is a tool that bootstraps a new Flask project
by creating the bare-minimum structure for a production ready project.
It is inspired by the `django-admin startproject` tool.
Running the tool prompts you for
- The project's name.
- The project's main app.
- The author's name and email.
- The project's description.

This is then used to create the project structure along with the necessary
`setup.py` for packaging your application.

# Installation
```shell
pip install flask-createproject
```

# Usage

```shell
flask-createproject
```
![](./media/demo.gif)

# Development
`pip-tools` is used for tracking the requirements and creating the development and release enviroments.

The requirements are kept in `requirements.in` and `requirements-dev.in` and compiled into `requirements.txt`
and `requirements-dev.txt` that could be later installed to the env.
A couple of useful `make` targets are defined.

## Creating the development environment.
```shell
python3.9 -m venv .venv
source .venv/bin/activate
make install-requirements-dev
```

## Adding a new requirement
1. add a new entry to the `requirements.in` or `requirements-dev.in` file (or both !)
2. run the command
```shell
make compile-requirements
```

## Running the tests.
1. Pytest is used and the configurations are defined in `setup.cfg`. 
2. You can run the tests by running the command
```shell
pytest
```

# Contribution
Please feel free to open Pull Requests/ issues as needed :-)