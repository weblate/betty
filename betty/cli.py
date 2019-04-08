import argparse
from tempfile import TemporaryDirectory

from betty.config import from_file
from betty.event import POST_PARSE_EVENT
from betty.gramps import parse
from betty.render import render
from betty.site import Site


def main():
    parser = argparse.ArgumentParser(
        description='Betty is a static ancestry site generator.')
    parser.add_argument('--config', dest='config_file_path',
                        required=True, action='store')

    parsed_args = parser.parse_args()
    try:
        with open(parsed_args.config_file_path) as f:
            configuration = from_file(f)
        with TemporaryDirectory() as working_directory_path:
            ancestry = parse(
                configuration.input_gramps_file_path, working_directory_path)
            site = Site(ancestry, configuration)
            site.event_dispatcher.dispatch(POST_PARSE_EVENT, ancestry)
            render(site)
    except KeyboardInterrupt:
        # Quit gracefully.
        print('Quitting...')
