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

- Python 3.12+
- Poetry for dependency management

## Installation

1. Clone the repository
2. Install dependencies using Poetry:

```bash
poetry install
```

## Usage

To run the tool, use the following command:

```bash
poetry run python main.py <input_file> <output_file>
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