"""
Provide configuration for the Wikipedia extension.
"""

from typing import Self

from typing_extensions import override

from betty.config import Configuration
from betty.serde.dump import Dump, VoidableDump, minimize, VoidableDumpMapping
from betty.assertion import (
    OptionalField,
    assert_record,
    assert_bool,
    assert_setattr,
)


class WikipediaConfiguration(Configuration):
    """
    Provides configuration for the :py:class:`betty.extension.wikipedia.Wikipedia` extension.
    """

    def __init__(self):
        super().__init__()
        self._populate_images = True

    @property
    def populate_images(self) -> bool:
        """
        Whether to populate entities with Wikimedia images after loading ancestries.
        """
        return self._populate_images

    @populate_images.setter
    def populate_images(self, populate_images: bool) -> None:
        self._populate_images = populate_images

    @override
    def update(self, other: Self) -> None:
        self._populate_images = other._populate_images

    @override
    def load(self, dump: Dump) -> None:
        assert_record(
            OptionalField(
                "populate_images",
                assert_bool() | assert_setattr(self, "populate_images"),
            )
        )(dump)

    @override
    def dump(self) -> VoidableDump:
        dump: VoidableDumpMapping[VoidableDump] = {
            "populate_images": self.populate_images,
        }
        return minimize(dump, True)
