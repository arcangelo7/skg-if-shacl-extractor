# SKG-IF SHACL Extractor

A Python tool to automatically generate SHACL shapes from OWL ontologies that follow the SKG-IF documentation pattern.

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

1. Clone the repository
2. Install dependencies using [Poetry](https://python-poetry.org/):

```bash
poetry install
```

## Usage

To run the tool, use the following command:

```bash
python -m main <input_file> <output_file>
```

where:
- `input_file`: Path to the input OWL ontology file in Turtle (.ttl) format. This file should contain class definitions with property descriptions following the SKG-IF documentation pattern.
- `output_file`: Path where the generated SHACL shapes will be saved (in Turtle format). The tool will create or overwrite this file.

Example:
```bash
python -m main ontology.ttl shapes.ttl
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