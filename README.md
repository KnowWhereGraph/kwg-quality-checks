# KWG-Graph-Quality-Tests
Knowledge Graph quality checks for KWG data

## Overview
This repository contains tests that are run against a Knowledge Graph, most likely the staging GraphDB deployment.
Each test file addresses a set of competency questions about a dataset, domain of thought, or aspect of triplification.

The repository is built as a set of unit tests which can be expanded on as the data changes.

## Configuring
The application config is set in the root `config.json`, where the endpoint and SPARQL prefixes can be set. New prefixes or
additional project functionality can be injected into this file.

## Running
The project is managed with poetry and requires at least Python 10.

To set up a virtual environment with Python 10 run the following
```commandline
pyenv install 3.10
pyenv local 3.10
```

To install dependencies and run the SPARQL queries against the database
```commandline
poetry install
poetry run pytest
```

To run an individual test
```commandline
poetry install
poetry run pytest tests/<your_test_.py>
```

For coverage statistics on the `quality_checks/` code, 
```commandline
poetry run pytest --cov=quality_checks/
```

## Contributing

### Adding Tests/Queries
New queries should be added as tests to an existing file if it seems to fit, otherwise in a new file in the `tests/` directory.

#### Testing Strategies
There are two suggested ways of testing the graph for content.

**Counting**
This is the recommended approach where the goal is to write a query that counts the number of results, based on some filter.
For example,

> Count the number of labels that contain unsupported charaters.

If the query returns anything greater than 0, it means that there are un-sanitized labels.

Another example is

> Count the number of administrative region level 2's that kwg-ont:sfOverlap

The query _should_ have a count of 0.

**Iterating**
Fetching all nodes that match some pattern is supported, but may be slow. Because GraphDB limits the number of
results, use the `QueryPaginator` class to paginate over all results.

### Code Style
The project makes use of a number of tools for code maintenance. Before committing changes, run the following
commands to process the files.
```commandline
poetry run isort .
poetry run black .
poetry run mypy .
poetry run flake518
```

### Submitting Pull Requests
Submit pull requests to the `main` branch with a small description of the changes and any additional testing steps.