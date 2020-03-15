from os.path import join
from tempfile import TemporaryDirectory
from unittest import TestCase

from betty.config import Configuration
from betty.plugin.maps import Maps
from betty.render import render
from betty.site import Site


class MapsTest(TestCase):
    def test_post_render_event(self):
        with TemporaryDirectory() as output_directory_path:
            configuration = Configuration(
                output_directory_path, 'https://ancestry.example.com')
            configuration.mode = 'development'
            configuration.plugins[Maps] = {}
            site = Site(configuration)
            render(site)
            with open(join(configuration.www_directory_path, 'maps.js')) as f:
                betty_js = f.read()
            self.assertIn('maps.js', betty_js)
            self.assertIn('maps.css', betty_js)
            with open(join(configuration.www_directory_path, 'maps.css')) as f:
                betty_css = f.read()
            self.assertIn('.map', betty_css)
