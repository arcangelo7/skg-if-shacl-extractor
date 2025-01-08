import argparse
import re
import os
from pathlib import Path
from typing import Optional

from rdflib import BNode, Graph, Literal, Namespace, URIRef
from rdflib.namespace import OWL, RDF, XSD

DEFAULT_ONTOLOGY_PATH = "data-model/current/skg-o.ttl"

def get_ontology_path(version: Optional[str] = None) -> str:
    """
    Get the path to the ontology file based on version.
    If version is None, returns the current version.
    """
    base_path = Path("data-model")
    
    if version is None:
        return str(base_path / "current" / "skg-o.ttl")
    
    version_path = base_path / version / "skg-o.ttl"
    if not version_path.exists():
        raise ValueError(f"Ontology version {version} not found at {version_path}")
    
    return str(version_path)

def create_shacl_shapes(input_file: str) -> Graph:
    g = Graph()
    g.parse(input_file, format='turtle', encoding='utf-8')
    
    shacl = Graph()
    SH = Namespace("http://www.w3.org/ns/shacl#")
    shacl.bind('sh', SH)
    
    for prefix, namespace in g.namespaces():
        shacl.bind(prefix, namespace)
    
    for cls in g.subjects(RDF.type, OWL.Class, unique=True):
        desc = g.value(cls, URIRef("http://purl.org/dc/elements/1.1/description"))
        if desc:
            shape_uri = URIRef(str(cls) + 'Shape')
            shacl.add((shape_uri, RDF.type, SH.NodeShape))
            shacl.add((shape_uri, SH.targetClass, cls))
            
            desc_str = str(desc)
            properties = desc_str.split("\n")[1:]

            for prop in properties:
                if not prop.strip():
                    continue
                    
                match = re.match(r'- ([\w:]+) -\[(\d+|\*)(\.\.)?(\d+|\*)?]->\s+([\w:]+)', prop.strip())
                if match:
                    prop_name, card_min, range_sep, card_max, target = match.groups()
                    bnode = BNode()
                    shacl.add((shape_uri, SH.property, bnode))
                    
                    if prop_name:
                        prefix, local = prop_name.split(':')
                        ns = str(g.store.namespace(prefix))
                        if ns:
                            prop_uri = URIRef(ns + local)
                            shacl.add((bnode, SH.path, prop_uri))
                        
                        if range_sep is None and card_min != '*':
                            exact_card = int(card_min)
                            shacl.add((bnode, SH.minCount, Literal(exact_card, datatype=XSD.integer)))
                            shacl.add((bnode, SH.maxCount, Literal(exact_card, datatype=XSD.integer)))
                        else:
                            if card_min and card_min != '*':
                                shacl.add((bnode, SH.minCount, Literal(int(card_min), datatype=XSD.integer)))
                            if card_max and card_max != '*':
                                shacl.add((bnode, SH.maxCount, Literal(int(card_max), datatype=XSD.integer)))
                        
                        if target:
                            target_prefix, target_local = target.split(':')
                            target_ns = str(g.store.namespace(target_prefix))
                            if target_ns:
                                target_uri = URIRef(target_ns + target_local)
                                if (target_uri, RDF.type, OWL.Class) in g:
                                    shacl.add((bnode, SH['class'], target_uri))
                                elif target == "rdfs:Literal":
                                    shacl.add((bnode, SH.nodeKind, SH.Literal))
                                elif target.startswith("xsd:"):
                                    shacl.add((bnode, SH.datatype, URIRef(f"http://www.w3.org/2001/XMLSchema#{target_local}")))
    
    return shacl

def main():
    parser = argparse.ArgumentParser(description='Convert SKG ontology to SHACL shapes')
    parser.add_argument('--input', help='Input TTL file path (optional)')
    parser.add_argument('--version', help='Ontology version (e.g., "1.0.0", "current")')
    parser.add_argument('output', help='Output SHACL file path')
    
    args = parser.parse_args()
    
    # If no input file is specified, use the versioned ontology
    if args.input:
        input_path = args.input
    else:
        try:
            input_path = get_ontology_path(args.version)
        except ValueError as e:
            parser.error(str(e))
    
    shacl_graph = create_shacl_shapes(input_path)
    shacl_graph.serialize(destination=args.output, format="turtle", encoding="utf-8")

if __name__ == "__main__": # pragma: no cover
    main()