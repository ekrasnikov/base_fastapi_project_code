# Base code
This repository contains base code.


## Getting Started
You need to have Docker with [docker-compose plugin](https://docs.docker.com/compose/install/linux/) installed on your machine (for example, [Docker Desktop](https://docs.docker.com/desktop/release-notes/)).

To start the application, simply clone the repo and run `docker compose up --build -d` in your local check-out. That command will build containers and run them locally. Once they're ready the API will be listening on `http://localhost:8000`.

If there are any pending migrations, run `docker compose exec api make run_migrations`.


## Development

You need to have Python3.12 installed on your machine (for example, [Python](https://www.python.org/downloads/release/python-3120/)).

pipenv should be installed and activated, [see](https://pipenv.pypa.io/en/latest/)

### Setup
Install dependencies for development `pipenv install --dev`
Install dependencies for deploy project `pipen install --ignore-pipfile`


### Testing
- If you need run tests, run <br> `make test`
- If you need run exact test, run <br> `PYTHONPATH=src ENV=pytest DEBUG=1 pytest -vv -x {test_path}`. <br> For example,<br>`PYTHONPATH=src ENV=pytest DEBUG=1 pytest -vv -x ./src/app/api/routers/test_auth_verify.py`

### Code Style
- To sort imports, run <br> `make beatify`
- If you need run linter, run <br> `make lint`

#### Example CLI
```
python app/cli.py base example-task
```
