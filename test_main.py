import shutil
import tempfile
import unittest
from pathlib import Path

from main import create_shacl_shapes
from rdflib import Literal, Namespace, URIRef
from rdflib.namespace import RDF


class TestTTLToSHACL(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(dir=".")
        self.test_data = '''
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix dc: <http://purl.org/dc/elements/1.1/> .
@prefix ex: <http://example.org/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

ex:TestClass a owl:Class ;
    dc:description """The properties that can be used with this class are:
- ex:stringProp -[1]-> xsd:string
- ex:intProp -[0..1]-> xsd:integer
- ex:objectProp -[1..*]-> ex:OtherClass
""" .

ex:OtherClass a owl:Class .
'''
        self.input_file = Path(self.temp_dir) / "test.ttl"
        with open(self.input_file, 'w', encoding='utf-8') as f:
            f.write(self.test_data)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_basic_shape_creation(self):
        shacl_graph = create_shacl_shapes(self.input_file)
        output_file = Path(self.temp_dir) / "basic_shape.ttl"
        shacl_graph.serialize(destination=output_file, format="turtle")
        
        SH = Namespace("http://www.w3.org/ns/shacl#")
        EX = Namespace("http://example.org/")
        shape_uri = URIRef("http://example.org/TestClassShape")
        
        self.assertIn((shape_uri, RDF.type, SH.NodeShape), shacl_graph)
        self.assertIn((shape_uri, SH.targetClass, EX.TestClass), shacl_graph)

    def test_property_constraints(self):
        shacl_graph = create_shacl_shapes(self.input_file)
        output_file = Path(self.temp_dir) / "property_constraints.ttl"
        shacl_graph.serialize(destination=output_file, format="turtle")
        
        SH = Namespace("http://www.w3.org/ns/shacl#")
        EX = Namespace("http://example.org/")
        XSD = Namespace("http://www.w3.org/2001/XMLSchema#")
        shape_uri = URIRef("http://example.org/TestClassShape")
        
        property_shapes = list(shacl_graph.objects(shape_uri, SH.property, unique=True))
        self.assertEqual(len(property_shapes), 3)
        
        props_found = {
            'stringProp': False,
            'intProp': False,
            'objectProp': False
        }
        
        for prop_shape in property_shapes:
            path = shacl_graph.value(prop_shape, SH.path)
            if path == EX.stringProp:
                props_found['stringProp'] = True
                self.assertIn((prop_shape, SH.datatype, XSD.string), shacl_graph)
                self.assertIn((prop_shape, SH.minCount, Literal(1)), shacl_graph)
                self.assertIn((prop_shape, SH.maxCount, Literal(1)), shacl_graph)
            elif path == EX.intProp:
                props_found['intProp'] = True
                self.assertIn((prop_shape, SH.datatype, XSD.integer), shacl_graph)
                self.assertIn((prop_shape, SH.maxCount, Literal(1)), shacl_graph)
            elif path == EX.objectProp:
                props_found['objectProp'] = True
                self.assertIn((prop_shape, SH["class"], EX.OtherClass), shacl_graph)
                self.assertIn((prop_shape, SH.minCount, Literal(1)), shacl_graph)
        
        self.assertTrue(all(props_found.values()))

    def test_no_description(self):
        no_desc_file = Path(self.temp_dir) / "no_desc.ttl"
        with open(no_desc_file, 'w', encoding='utf-8') as f:
            f.write("""
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix ex: <http://example.org/> .

ex:NoDescClass a owl:Class .
""")
            
        shacl_graph = create_shacl_shapes(no_desc_file)
        output_file = Path(self.temp_dir) / "no_description.ttl"
        shacl_graph.serialize(destination=output_file, format="turtle")
        
        self.assertEqual(len(list(shacl_graph.subjects(RDF.type, URIRef("http://www.w3.org/ns/shacl#NodeShape")))), 0)

if __name__ == '__main__':
    unittest.main()