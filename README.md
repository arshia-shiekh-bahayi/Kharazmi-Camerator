# Camerator

Number one solution for photographers

## Setup Project

Install Docker, Docker Compose and MYPY and you are done!

### Use `project.py` script

- To run the project, simply execute this command: `pipenv run python project.py start -d`
- To populate the initial data, you can use populate command: `pipenv run python project.py populate`
- To get access to the project's shell, use this command: `pipenv run python project.py shell`
- To run django commands like migrations, use this command: `pipenv run python project.py django [django_command]`
- To stop the project, use stop command: `pipenv run python project.py stop`
- To run mypy type checker, use mypy command: `pipenv run python project.py mypy`

### Type checks

Running type checks with mypy:

    $ cd camerator && mypy --explicit-package-bases . --config-file=mypy.ini

### Celery, Redis and PostgreSQL

This app comes with Celery, Redis and PostgreSQL as a docker containers. Which means you don't need to do anything,
just run the docker containers (defined in `local.yml`) and everything will be setup for you automatically.

## Setup Development

### pre-commit

- Install Docker and Docker Compose
- Clone project to your system: `git clone ...`
- Open project in your favorite IDE or Text Editor
- Install [pre-commit](https://pre-commit.com/) on your system
- Install pre-commit hooks: `pipenv run pre-commit install && pipenv run pre-commit install --hook-type pre-push`

## Project initial data

Load data from fixtures by running:

```shell
pipenv run python project.py django loaddata data.json
```

This will create a new user with username `09123456789` and password `admin` for you.

## Development guideline

- Write unittests for endpoints and models only
- Install pre-commit
- Always create PR to branch `dev`
- Your branch name should follow this pattern: `{your_name}/{feature_or_bug_code}_{descriptive_name}` prefix.
  For example: `mohsen/12_fix_login_issue`
- Each viewset should have its own file with its required serializers
- Business logic should be inside serializers
- Use pep8 style guide
