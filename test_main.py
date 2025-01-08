import shutil
import tempfile
import unittest
from pathlib import Path
import unittest.mock

from rdflib import Literal, Namespace, URIRef, Graph
from rdflib.namespace import RDF
from src.main import create_shacl_shapes, get_ontology_path


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
- ex:literalProp -[1]-> rdfs:Literal
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
        shacl_graph.serialize(destination=output_file, format="turtle", encoding="utf-8")
        
        SH = Namespace("http://www.w3.org/ns/shacl#")
        EX = Namespace("http://example.org/")
        shape_uri = URIRef("http://example.org/TestClassShape")
        
        self.assertIn((shape_uri, RDF.type, SH.NodeShape), shacl_graph)
        self.assertIn((shape_uri, SH.targetClass, EX.TestClass), shacl_graph)

    def test_property_constraints(self):
        shacl_graph = create_shacl_shapes(self.input_file)
        output_file = Path(self.temp_dir) / "property_constraints.ttl"
        shacl_graph.serialize(destination=output_file, format="turtle", encoding="utf-8")
        
        SH = Namespace("http://www.w3.org/ns/shacl#")
        EX = Namespace("http://example.org/")
        XSD = Namespace("http://www.w3.org/2001/XMLSchema#")
        shape_uri = URIRef("http://example.org/TestClassShape")
        
        property_shapes = list(shacl_graph.objects(shape_uri, SH.property, unique=True))
        self.assertEqual(len(property_shapes), 4)
        
        props_found = {
            'stringProp': False,
            'intProp': False,
            'objectProp': False,
            'literalProp': False
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
            elif path == EX.literalProp:
                props_found['literalProp'] = True
                self.assertIn((prop_shape, SH.nodeKind, SH.Literal), shacl_graph)
                self.assertIn((prop_shape, SH.minCount, Literal(1)), shacl_graph)
                self.assertIn((prop_shape, SH.maxCount, Literal(1)), shacl_graph)
        
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
        shacl_graph.serialize(destination=output_file, format="turtle", encoding="utf-8")
        
        self.assertEqual(len(list(shacl_graph.subjects(RDF.type, URIRef("http://www.w3.org/ns/shacl#NodeShape")))), 0)

    def test_main_function(self):
        input_file = self.input_file
        output_file = Path(self.temp_dir) / "test_main_output.ttl"
        
        test_args = ['prog_name', '--input', str(input_file), str(output_file)]
        with unittest.mock.patch('sys.argv', test_args):
            from src.main import main
            main()
        
        self.assertTrue(output_file.exists())
        g = Graph()
        g.parse(output_file, format='turtle')
        
        SH = Namespace("http://www.w3.org/ns/shacl#")
        self.assertTrue(any(s for s in g.subjects(RDF.type, SH.NodeShape)))

    def test_get_ontology_path_with_version(self):
        """Test get_ontology_path with a specific version"""
        version = "1.0.0"
        expected_path = str(Path("data-model") / "ontology" / "1.0.0" / "skg-o.ttl")
        actual_path = get_ontology_path(version)
        self.assertEqual(actual_path, expected_path)

    def test_get_ontology_path_current(self):
        """Test get_ontology_path with no version (should return current)"""
        expected_path = str(Path("data-model") / "ontology" / "current" / "skg-o.ttl")
        actual_path = get_ontology_path()
        self.assertEqual(actual_path, expected_path)

    def test_get_ontology_path_invalid_version(self):
        """Test get_ontology_path with an invalid version"""
        invalid_version = "999.999.999"
        with self.assertRaises(ValueError) as context:
            get_ontology_path(invalid_version)
        self.assertIn("Ontology version 999.999.999 not found", str(context.exception))

    def test_version_argument_in_main(self):
        """Test main function with version argument"""
        output_file = Path(self.temp_dir) / "version_test_output.ttl"
        
        test_args = ['prog_name', '--version', '1.0.0', str(output_file)]
        with unittest.mock.patch('sys.argv', test_args):
            from src.main import main
            main()
        
        self.assertTrue(output_file.exists())
        g = Graph()
        g.parse(output_file, format='turtle')
        
        SH = Namespace("http://www.w3.org/ns/shacl#")
        self.assertTrue(any(s for s in g.subjects(RDF.type, SH.NodeShape)))

if __name__ == '__main__':
    unittest.main()