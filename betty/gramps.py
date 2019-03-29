import gzip
import tarfile
from os.path import join, dirname
from typing import Dict, Tuple, List, Optional

from geopy import Point
from lxml import etree
from lxml.etree import XMLParser, Element

from betty.ancestry import Document, Event, Place, Family, Person, Ancestry, Date, Note, File

NS = {
    'ns': 'http://gramps-project.org/xml/1.7.1/',
}


def xpath(element, selector: str) -> []:
    return element.xpath(selector, namespaces=NS)


def xpath1(element, selector: str) -> []:
    elements = element.xpath(selector, namespaces=NS)
    if elements:
        return elements[0]
    return None


def parse(gramps_file_path, working_directory_path) -> Ancestry:
    ungzipped_outer_file = gzip.open(gramps_file_path)
    xml_file_path = join(working_directory_path, 'data.xml')
    with open(xml_file_path, 'wb') as xml_file:
        try:
            tarfile.open(fileobj=ungzipped_outer_file).extractall(working_directory_path)
            gramps_file_path = join(working_directory_path, 'data.gramps')
            xml_file.write(gzip.open(gramps_file_path).read())
        except tarfile.ReadError:
            xml_file.write(ungzipped_outer_file.read())

    return _parse_xml_file(xml_file_path)


def _parse_xml_file(file_path) -> Ancestry:
    parser = XMLParser()
    tree = etree.parse(file_path, parser)
    database = tree.getroot()
    notes = _parse_notes(database)
    documents = _parse_documents(file_path, notes, database)
    places = _parse_places(database)
    events = _parse_events(places, database)
    people = _parse_people(events, database)
    families = _parse_families(people, documents, database)
    ancestry = Ancestry()
    ancestry.documents = {document.id: document for document in documents.values()}
    ancestry.people = {person.id: person for person in people.values()}
    ancestry.families = {family.id: family for family in families.values()}
    ancestry.places = {place.id: place for place in places.values()}
    ancestry.events = {event.id: event for event in events.values()}
    return ancestry


def _parse_date(element: Element) -> Optional[Date]:
    dateval = xpath1(element, './ns:dateval/@val')
    if dateval:
        dateval_components = dateval.split('-')
        date_components = [int(val) for val in dateval_components] + \
                          [None] * (3 - len(dateval_components))
        return Date(*date_components)
    return None


def _parse_notes(database: Element) -> Dict[str, Note]:
    return {handle: note for handle, note in
            [_parse_note(element) for element in xpath(database, './ns:notes/ns:note')]}


def _parse_note(element: Element) -> Tuple[str, Note]:
    handle = xpath1(element, './@handle')
    text = xpath1(element, './ns:text/text()')
    return handle, Note(text)


def _parse_documents(gramps_file_path: str, notes: Dict[str, Note], database: Element) -> Dict[str, Document]:
    return {handle: document for handle, document in
            [_parse_document(gramps_file_path, notes, element) for element in
             xpath(database, './ns:objects/ns:object')]}


def _parse_document(gramps_file_path, notes: Dict[str, Note], element: Element) -> Tuple[str, Document]:
    handle = xpath1(element, './@handle')
    entity_id = xpath1(element, './@id')
    file_element = xpath1(element, './ns:file')
    file_path = join(dirname(gramps_file_path), xpath1(file_element, './@src'))
    file = File(file_path)
    file.type = xpath1(file_element, './@mime')
    note_handles = xpath(element, './ns:noteref/@hlink')
    document = Document(entity_id, file)
    description = xpath1(file_element, './@description')
    if description:
        document.description = description
    for note_handle in note_handles:
        document.notes.append(notes[note_handle])
    return handle, document


def _parse_people(events: Dict[str, Event], database: Element) -> Dict[str, Person]:
    return {handle: person for handle, person in
            [_parse_person(events, element) for element in database.xpath('.//*[local-name()="person"]')]}


def _parse_person(events: Dict[str, Event], element: Element) -> Tuple[str, Person]:
    handle = xpath1(element, './@handle')
    properties = {
        'individual_name': element.xpath('./ns:name[@type="Birth Name"]/ns:first', namespaces=NS)[0].text,
        'family_name': element.xpath('./ns:name[@type="Birth Name"]/ns:surname', namespaces=NS)[0].text,
    }
    event_handles = xpath(element, './ns:eventref/@hlink')
    person = Person(element.xpath('./@id')[0], **properties)
    for event_handle in event_handles:
        person.events.add(events[event_handle])
    return handle, person


def _parse_person_birth(events: Dict[str, Event], handles: List[str]) -> Optional[Event]:
    births = _parse_person_filter_events(events, handles, Event.Type.BIRTH)
    return births[0] if births else None


def _parse_person_death(events: Dict[str, Event], handles: List[str]) -> Optional[Event]:
    births = _parse_person_filter_events(events, handles, Event.Type.DEATH)
    return births[0] if births else None


def _parse_person_filter_events(events: Dict[str, Event], handles: List[str], event_type: Event.Type) -> List[Event]:
    return [event for event in [events[event_handle] for event_handle in handles] if event.type == event_type]


def _parse_families(people: Dict[str, Person], documents: Dict[str, Document], database: Element) -> Dict[str, Family]:
    return {family.id: family for family in
            [_parse_family(people, documents, element) for element in database.xpath('.//*[local-name()="family"]')]}


def _parse_family(people: Dict[str, Person], documents: Dict[str, Document], element: Element) -> Family:
    family = Family(element.xpath('./@id')[0])

    # Parse the father.
    father_handle = xpath1(element, './ns:father/@hlink')
    if father_handle:
        father = people[father_handle]
        father.ancestor_families.add(family)
        family.parents.add(father)

    # Parse the mother.
    mother_handle = xpath1(element, './ns:mother/@hlink')
    if mother_handle:
        mother = people[mother_handle]
        mother.ancestor_families.add(family)
        family.parents.add(mother)

    # Parse the children.
    child_handles = xpath(element, './ns:childref/@hlink')
    for child_handle in child_handles:
        child = people[child_handle]
        child.descendant_family = family
        family.children.add(child)

    # Parse the documents.
    document_handles = xpath(element, './ns:objref/@hlink')
    for document_handle in document_handles:
        family.documents.append(documents[document_handle])

    return family


class _IntermediatePlace:
    def __init__(self, place: Place, enclosed_by_handle: Optional[str]):
        self.place = place
        self.enclosed_by_handle = enclosed_by_handle


def _parse_places(database: Element) -> Dict[str, Place]:
    intermediate_places = {handle: intermediate_place for handle, intermediate_place in
                           [_parse_place(element) for element in database.xpath('.//*[local-name()="placeobj"]')]}
    for intermediate_place in intermediate_places.values():
        if intermediate_place.enclosed_by_handle is not None:
            intermediate_place.place.enclosed_by = intermediate_places[intermediate_place.enclosed_by_handle].place
    return {handle: intermediate_place.place for handle, intermediate_place in intermediate_places.items()}


def _parse_place(element: Element) -> Tuple[str, _IntermediatePlace]:
    handle = xpath1(element, './@handle')
    properties = {
        'name': element.xpath('./ns:pname/@value', namespaces=NS)[0]
    }
    place = Place(element.xpath('./@id')[0], **properties)

    coordinates = _parse_coordinates(element)
    if coordinates:
        place.coordinates = coordinates

    # Set the first place reference as the place that encloses this place.
    enclosed_by_handle = xpath1(element, './ns:placeref/@hlink')

    return handle, _IntermediatePlace(place, enclosed_by_handle)


def _parse_coordinates(element: Element) -> Optional[Point]:
    coord_element = xpath1(element, './ns:coord')

    if coord_element is None:
        return None

    latitudeval = xpath1(coord_element, './@lat')
    longitudeval = xpath1(coord_element, './@long')

    try:
        return Point(latitudeval, longitudeval)
    except BaseException:
        # We could not parse/validate the Gramps coordinates, because they are too freeform.
        pass
    return None


def _parse_events(places: Dict[str, Place], database: Element) -> Dict[str, Event]:
    return {handle: event for handle, event in
            [_parse_event(places, element) for element in database.xpath('.//*[local-name()="event"]')]}


EVENT_TYPE_MAP = {
    'Birth': Event.Type.BIRTH,
    'Death': Event.Type.DEATH,
    'Burial': Event.Type.BURIAL,
    'Marriage': Event.Type.MARRIAGE,
}


def _parse_event(places: Dict[str, Place], element: Element) -> Tuple[str, Event]:
    handle = xpath1(element, './@handle')
    gramps_type = xpath1(element, './ns:type')

    event = Event(xpath1(element, './@id'), EVENT_TYPE_MAP[gramps_type.text])

    event.date = _parse_date(element)

    # Parse the event place.
    place_handle = xpath1(element, './ns:place/@hlink')
    if place_handle:
        event.place = places[place_handle]

    return handle, event
