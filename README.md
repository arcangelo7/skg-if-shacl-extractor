# SKG-IF SHACL Extractor

[![Tests](https://github.com/arcangelo7/skg-if-shacl-extractor/actions/workflows/tests.yml/badge.svg)](https://github.com/arcangelo7/skg-if-shacl-extractor/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/arcangelo7/skg-if-shacl-extractor/branch/main/graph/badge.svg)](https://codecov.io/gh/arcangelo7/skg-if-shacl-extractor)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: ISC](https://img.shields.io/badge/License-ISC-blue.svg)](https://opensource.org/licenses/ISC)
[![Poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json)](https://python-poetry.org/)

A Python tool to automatically generate SHACL shapes from OWL ontologies that follow the SKG-IF documentation pattern. The SKG-IF data model is documented at https://skg-if.github.io/data-model/.

## Description

This tool extracts SHACL (Shapes Constraint Language) shapes from OWL ontologies that use a specific documentation pattern for describing class properties. It parses property descriptions in the format:

- propertyName -[cardinality]-> targetType

For example:

- dcterms:title -[1]-> rdfs:Literal
- frapo:hasGrantNumber -[0..1]-> xsd:string
- frapo:hasFundingAgency -[0..1]-> frapo:FundingAgency

## Requirements

- Python 3.9+
- Poetry for dependency management

## Installation

1. Clone the repository with its submodules:

```bash
git clone --recurse-submodules https://github.com/arcangelo7/skg-if-shacl-extractor.git
```

2. Install dependencies using [Poetry](https://python-poetry.org/):

```bash
poetry install
```

## Usage

To run the tool, use the following command:

```bash
poetry run extractor <input_file> <output_file>
```

Or if you want to run it directly:

```bash
python -m src.main <input_file> <output_file>
```

where:
- `input_file`: Path to the input OWL ontology file in Turtle (.ttl) format. This file should contain class definitions with property descriptions following the SKG-IF documentation pattern.
- `output_file`: Path where the generated SHACL shapes will be saved (in Turtle format). The tool will create or overwrite this file.

Example:
```bash
poetry run extractor ontology.ttl shapes.ttl
```

## Testing

Run the unit tests:

```bash
python -m unittest
```

## License

ISC License

## Author

Arcangelo Massari (arcangelo.massari@unibo.it)