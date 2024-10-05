"""
Define and provide key-value mappings of :py:class:`betty.config.Configuration` instances.
"""

from __future__ import annotations

from abc import abstractmethod
from collections.abc import Mapping
from contextlib import suppress
from typing import (
    Generic,
    Iterable,
    Iterator,
    Self,
    TypeVar,
    TYPE_CHECKING,
)

from typing_extensions import override

from betty.assertion import assert_sequence, assert_mapping
from betty.config import Configuration
from betty.config.collections import ConfigurationCollection, ConfigurationKey
from betty.serde.dump import (
    Dump,
    minimize,
    DumpMapping,
    DumpSequence,
)
from betty.typing import Void, Voidable

if TYPE_CHECKING:
    from collections.abc import MutableMapping

_ConfigurationT = TypeVar("_ConfigurationT", bound=Configuration)
_ConfigurationKeyT = TypeVar("_ConfigurationKeyT", bound=ConfigurationKey)


class _ConfigurationMapping(
    ConfigurationCollection[_ConfigurationKeyT, _ConfigurationT],
    Generic[_ConfigurationKeyT, _ConfigurationT],
):
    def __init__(
        self,
        configurations: Iterable[_ConfigurationT] | None = None,
    ):
        self._configurations: MutableMapping[_ConfigurationKeyT, _ConfigurationT] = {}
        super().__init__(configurations)

    def _void_minimized_item_dump(self) -> bool:
        return False

    @override
    def __getitem__(self, configuration_key: _ConfigurationKeyT) -> _ConfigurationT:
        return self._configurations[configuration_key]

    @override
    def __iter__(self) -> Iterator[_ConfigurationKeyT]:
        return (configuration_key for configuration_key in self._configurations)

    @override
    def keys(self) -> Iterator[_ConfigurationKeyT]:
        return (configuration_key for configuration_key in self._configurations)

    @override
    def values(self) -> Iterator[_ConfigurationT]:
        yield from self._configurations.values()

    @override
    def update(self, other: Self) -> None:
        self.replace(*other.values())

    @override
    def replace(self, *configurations: _ConfigurationT) -> None:
        self.clear()
        self.append(*configurations)

    @override
    def prepend(self, *configurations: _ConfigurationT) -> None:
        self.insert(0, *configurations)

    @override
    def append(self, *configurations: _ConfigurationT) -> None:
        for configuration in configurations:
            configuration_key = self._get_key(configuration)
            with suppress(KeyError):
                del self._configurations[configuration_key]
            self._configurations[configuration_key] = configuration

    @override
    def insert(self, index: int, *configurations: _ConfigurationT) -> None:
        self.remove(*map(self._get_key, configurations))
        existing_configurations = list(self.values())
        self._configurations = {
            self._get_key(configuration): configuration
            for configuration in (
                *existing_configurations[:index],
                *configurations,
                *existing_configurations[index:],
            )
        }

    @abstractmethod
    def _get_key(self, configuration: _ConfigurationT) -> _ConfigurationKeyT:
        pass


class ConfigurationMapping(
    _ConfigurationMapping[_ConfigurationKeyT, _ConfigurationT],
    Generic[_ConfigurationKeyT, _ConfigurationT],
):
    """
    A key-value mapping where values are :py:class:`betty.config.Configuration`.

    To test your own subclasses, use :py:class:`betty.test_utils.config.collections.mapping.ConfigurationMappingTestBase`.
    """

    @abstractmethod
    async def _load_key(self, item_dump: DumpMapping[Dump], key_dump: str) -> None:
        pass

    @abstractmethod
    def _dump_key(self, item_dump: DumpMapping[Dump]) -> str:
        pass

    async def __load_item_key(
        self, value_dump: DumpMapping[Dump], key_dump: str
    ) -> Dump:
        await self._load_key(value_dump, key_dump)
        return value_dump

    @override
    async def load(self, dump: Dump) -> None:
        self.clear()
        self.replace(
            *await assert_mapping(self.load_item)(
                {
                    item_key_dump: self.__load_item_key(item_value_dump, item_key_dump)
                    for item_key_dump, item_value_dump in (
                        await assert_mapping(assert_mapping())(dump)
                    ).items()
                }
            ).values()
        )

    @override
    def dump(self) -> Voidable[DumpMapping[Dump]]:
        dump = {}
        for configuration_item in self._configurations.values():
            item_dump = configuration_item.dump()
            if item_dump is not Void:
                assert isinstance(item_dump, Mapping)
                configuration_key = self._dump_key(item_dump)
                item_dump = minimize(item_dump, self._void_minimized_item_dump())
                dump[configuration_key] = item_dump
        return minimize(dump, True)


class OrderedConfigurationMapping(
    _ConfigurationMapping[_ConfigurationKeyT, _ConfigurationT],
    Generic[_ConfigurationKeyT, _ConfigurationT],
):
    """
    An ordered key-value mapping where values are :py:class:`betty.config.Configuration`.

    To test your own subclasses, use :py:class:`betty.test_utils.config.collections.mapping.OrderedConfigurationMappingTestBase`.
    """

    @override
    async def load(self, dump: Dump) -> None:
        self.replace(*await assert_sequence(self.load_item)(dump))

    @override
    def dump(self) -> Voidable[DumpSequence[Dump]]:
        return minimize(
            [
                configuration_item.dump()
                for configuration_item in self._configurations.values()
            ],
            True,
        )
