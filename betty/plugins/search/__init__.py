from os.path import dirname
from typing import Optional, Iterable, Callable, Dict

from betty.ancestry import Person, Place, File
from betty.jinja2 import Jinja2Provider, create_environment
from betty.plugin import Plugin
from betty.plugins.js import Js, JsEntryPointProvider, JsPackageProvider
from betty.site import Site


class Search(Plugin, JsPackageProvider, JsEntryPointProvider, Jinja2Provider):
    def __init__(self, site: Site):
        self._site = site

    @classmethod
    def depends_on(cls):
        return {Js}

    @classmethod
    def from_configuration_dict(cls, site: Site, configuration: Dict):
        return cls(site)

    @property
    def resource_directory_path(self) -> Optional[str]:
        return '%s/resources' % dirname(__file__)

    @property
    def globals(self) -> Dict[str, Callable]:
        return {
            'search_index': lambda: index(self._site),
        }


def index(site: Site) -> Iterable:
    # Create the environments here, because doing so in the initializer would be at a time when not all plugins have
    # been initialized yet
    environments = {}
    for locale in site.configuration.locales:
        environments[locale] = create_environment(site, locale)

    def render_person_result(locale: str, person: Person):
        return environments[locale].get_template('search-result-person.html.j2').render({
            'person': person,
        })
    for person in site.ancestry.people.values():
        if person.private:
            continue
        names = []
        for name in person.names:
            if name.individual is not None:
                names.append(name.individual.lower())
            if name.affiliation is not None:
                names.append(name.affiliation.lower())
        if names:
            yield {
                'text': ' '.join(names),
                'results': {locale: render_person_result(locale, person) for locale in environments},
            }

    def render_place_result(locale: str, place: Place):
        return environments[locale].get_template('search-result-place.html.j2').render({
            'place': place,
        })
    for file in site.ancestry.places.values():
        yield {
            'text': ' '.join(map(lambda x: x.name.lower(), file.names)),
            'results': {locale: render_place_result(locale, file) for locale in environments},
        }

    def render_file_result(locale: str, file: File):
        return environments[locale].get_template('search-result-file.html.j2').render({
            'file': file,
        })
    for file in site.ancestry.files.values():
        yield {
            'text': file.description.lower(),
            'results': {locale: render_file_result(locale, file) for locale in environments},
        }
