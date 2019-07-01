from os.path import join, dirname, abspath
from tempfile import TemporaryDirectory
from unittest import TestCase

from lxml import etree
from lxml.etree import XMLParser

from betty.ancestry import Event, Ancestry
from betty.config import Configuration
from betty.parse import parse
from betty.plugins.gramps import extract_xml_file, parse_xml_file, Gramps
from betty.site import Site


class ExtractXmlFileTest(TestCase):
    def test_gramps_xml(self):
        with TemporaryDirectory() as cache_directory_path:
            gramps_file_path = join(
                dirname(abspath(__file__)), 'resources', 'minimal.gramps')
            xml_file_path = extract_xml_file(
                gramps_file_path, cache_directory_path)
            with open(xml_file_path) as f:
                parser = XMLParser()
                etree.parse(f, parser)

    def test_portable_gramps_xml_package(self):
        with TemporaryDirectory() as cache_directory_path:
            gramps_file_path = join(
                dirname(abspath(__file__)), 'resources', 'minimal.gpkg')
            xml_file_path = extract_xml_file(
                gramps_file_path, cache_directory_path)
            with open(xml_file_path) as f:
                parser = XMLParser()
                etree.parse(f, parser)


class ParseXmlFileTestCase(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.ancestry = Ancestry()
        parse_xml_file(cls.ancestry, join(
            dirname(abspath(__file__)), 'resources', 'data.xml'))

    def test_place_should_include_name(self):
        place = self.ancestry.places['P0000']
        self.assertEquals('Amsterdam', place.name)

    def test_place_should_include_coordinates(self):
        place = self.ancestry.places['P0000']
        self.assertAlmostEquals(52.366667, place.coordinates.latitude)
        self.assertAlmostEquals(4.9, place.coordinates.longitude)

    def test_place_should_include_events(self):
        place = self.ancestry.places['P0000']
        event = self.ancestry.events['E0000']
        self.assertIn(event, place.events)

    def test_person_should_include_individual_name(self):
        person = self.ancestry.people['I0000']
        self.assertEquals('Jane', person.individual_name)
        self.assertEquals('Doe', person.family_name)

    def test_person_should_include_birth(self):
        person = self.ancestry.people['I0000']
        self.assertEquals('E0000', person.birth.id)

    def test_person_should_include_death(self):
        person = self.ancestry.people['I0003']
        self.assertEquals('E0002', person.death.id)

    def test_person_should_be_private(self):
        person = self.ancestry.people['I0003']
        self.assertTrue(person.private)

    def test_person_should_not_be_private(self):
        person = self.ancestry.people['I0002']
        self.assertFalse(person.private)

    def test_person_should_include_citation(self):
        person = self.ancestry.people['I0000']
        source = self.ancestry.references['C0000']
        self.assertIn(source, person.references)

    def test_family_should_set_parents(self):
        expected_parents = [self.ancestry.people['I0002'],
                            self.ancestry.people['I0003']]
        children = [self.ancestry.people['I0000'],
                    self.ancestry.people['I0001']]
        for child in children:
            self.assertCountEqual(expected_parents, child.parents)

    def test_family_should_set_children(self):
        parents = [self.ancestry.people['I0002'],
                   self.ancestry.people['I0003']]
        expected_children = [self.ancestry.people['I0000'],
                             self.ancestry.people['I0001']]
        for parent in parents:
            self.assertCountEqual(expected_children, parent.children)

    def test_event_should_be_birth(self):
        self.assertEquals(Event.Type.BIRTH, self.ancestry.events['E0000'].type)

    def test_event_should_be_death(self):
        self.assertEquals(Event.Type.DEATH, self.ancestry.events['E0002'].type)

    def test_event_should_include_place(self):
        event = self.ancestry.events['E0000']
        place = self.ancestry.places['P0000']
        self.assertEquals(place, event.place)

    def test_event_should_include_date(self):
        event = self.ancestry.events['E0000']
        self.assertEquals(1970, event.date.year)
        self.assertEquals(1, event.date.month)
        self.assertEquals(1, event.date.day)

    def test_event_should_include_people(self):
        event = self.ancestry.events['E0000']
        expected_people = [self.ancestry.people['I0000']]
        self.assertCountEqual(expected_people, event.people)

    def test_date_should_ignore_invalid_date(self):
        date = self.ancestry.events['E0001'].date
        self.assertIsNone(date)

    def test_date_should_ignore_invalid_date_parts(self):
        date = self.ancestry.events['E0002'].date
        self.assertIsNotNone(date)
        self.assertIsNone(date.year)
        self.assertEquals(12, date.month)
        self.assertEquals(31, date.day)

    def test_source_from_repository_should_include_name(self):
        source = self.ancestry.references['R0000']
        self.assertEquals('Library of Alexandria', source.name)

    def test_source_from_repository_should_include_link(self):
        link = self.ancestry.references['R0000'].link
        self.assertEquals('https://alexandria.example.com', link.uri)
        self.assertEquals('Library of Alexandria Catalogue', link.label)

    def test_source_from_source_should_include_title(self):
        source = self.ancestry.references['S0000']
        self.assertEquals('A Whisper', source.name)

    def test_source_from_source_should_include_repository(self):
        source = self.ancestry.references['S0000']
        containing_source = self.ancestry.references['R0000']
        self.assertEquals(containing_source, source.contained_by)


class GrampsTest(TestCase):
    def test_parse_event(self):
        with TemporaryDirectory() as output_directory_path:
            configuration = Configuration(
                output_directory_path, 'https://example.com')
            configuration.plugins[Gramps] = {
                'file': join(dirname(abspath(__file__)), 'resources', 'minimal.gpkg')
            }
            site = Site(configuration)
            parse(site)
            self.assertEquals(
                'Dough', site.ancestry.people['I0000'].family_name)
            self.assertEquals(
                'Janet', site.ancestry.people['I0000'].individual_name)
            self.assertEquals(
                '1px', site.ancestry.files['O0000'].description)