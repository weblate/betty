from __future__ import annotations

from typing import Any, TYPE_CHECKING

import pytest
from betty.model import Entity
from betty.model.ancestry import Person
from betty.model.collections import (
    SingleTypeEntityCollection,
    MultipleTypesEntityCollection,
)
from betty.plugin import PluginNotFound
from betty.plugin.static import StaticPluginRepository

from betty.test_utils.model import DummyEntity

if TYPE_CHECKING:
    from pytest_mock import MockerFixture


class SingleTypeEntityCollectionTestEntity(DummyEntity):
    pass


class TestSingleTypeEntityCollection:
    async def test_add(self) -> None:
        sut = SingleTypeEntityCollection[Entity](DummyEntity)
        entity1 = SingleTypeEntityCollectionTestEntity()
        entity2 = SingleTypeEntityCollectionTestEntity()
        entity3 = SingleTypeEntityCollectionTestEntity()
        sut.add(entity3)
        sut.add(entity2)
        sut.add(entity1)
        # Add an already added value again, and assert that it was ignored.
        sut.add(entity1)
        assert [entity3, entity2, entity1] == list(sut)

    async def test_add_with_duplicate_entities(self) -> None:
        sut = SingleTypeEntityCollection[Entity](DummyEntity)
        entity1 = SingleTypeEntityCollectionTestEntity()
        entity2 = SingleTypeEntityCollectionTestEntity()
        entity3 = SingleTypeEntityCollectionTestEntity()
        entity4 = SingleTypeEntityCollectionTestEntity()
        entity5 = SingleTypeEntityCollectionTestEntity()
        entity6 = SingleTypeEntityCollectionTestEntity()
        entity7 = SingleTypeEntityCollectionTestEntity()
        entity8 = SingleTypeEntityCollectionTestEntity()
        entity9 = SingleTypeEntityCollectionTestEntity()
        # Ensure duplicates are skipped.
        sut.add(
            entity1,
            entity2,
            entity3,
            entity1,
            entity2,
            entity3,
            entity1,
            entity2,
            entity3,
        )
        assert [entity1, entity2, entity3] == list(sut)
        # Ensure skipped duplicates do not affect further new values.
        sut.add(
            entity1,
            entity2,
            entity3,
            entity4,
            entity5,
            entity6,
            entity7,
            entity8,
            entity9,
        )
        assert [
            entity1,
            entity2,
            entity3,
            entity4,
            entity5,
            entity6,
            entity7,
            entity8,
            entity9,
        ] == list(sut)

    async def test_remove(self) -> None:
        sut = SingleTypeEntityCollection[Entity](DummyEntity)
        entity1 = SingleTypeEntityCollectionTestEntity()
        entity2 = SingleTypeEntityCollectionTestEntity()
        entity3 = SingleTypeEntityCollectionTestEntity()
        entity4 = SingleTypeEntityCollectionTestEntity()
        sut.add(entity1, entity2, entity3, entity4)
        sut.remove(entity4, entity2)
        assert [entity1, entity3] == list(sut)

    async def test_replace(self) -> None:
        sut = SingleTypeEntityCollection[Entity](DummyEntity)
        entity1 = SingleTypeEntityCollectionTestEntity()
        entity2 = SingleTypeEntityCollectionTestEntity()
        entity3 = SingleTypeEntityCollectionTestEntity()
        entity4 = SingleTypeEntityCollectionTestEntity()
        entity5 = SingleTypeEntityCollectionTestEntity()
        entity6 = SingleTypeEntityCollectionTestEntity()
        sut.add(entity1, entity2, entity3)
        sut.replace(entity4, entity5, entity6)
        assert [entity4, entity5, entity6] == list(sut)

    async def test_clear(self) -> None:
        sut = SingleTypeEntityCollection[Entity](DummyEntity)
        entity1 = SingleTypeEntityCollectionTestEntity()
        entity2 = SingleTypeEntityCollectionTestEntity()
        entity3 = SingleTypeEntityCollectionTestEntity()
        sut.add(entity1, entity2, entity3)
        sut.clear()
        assert list(sut) == []

    async def test_list(self) -> None:
        sut = SingleTypeEntityCollection[Entity](DummyEntity)
        entity1 = SingleTypeEntityCollectionTestEntity()
        entity2 = SingleTypeEntityCollectionTestEntity()
        entity3 = SingleTypeEntityCollectionTestEntity()
        sut.add(entity1, entity2, entity3)
        assert entity1 is sut[0]
        assert entity2 is sut[1]
        assert entity3 is sut[2]

    async def test_len(self) -> None:
        sut = SingleTypeEntityCollection[Entity](DummyEntity)
        entity1 = SingleTypeEntityCollectionTestEntity()
        entity2 = SingleTypeEntityCollectionTestEntity()
        entity3 = SingleTypeEntityCollectionTestEntity()
        sut.add(entity1, entity2, entity3)
        assert len(sut) == 3

    async def test_iter(self) -> None:
        sut = SingleTypeEntityCollection[Entity](DummyEntity)
        entity1 = SingleTypeEntityCollectionTestEntity()
        entity2 = SingleTypeEntityCollectionTestEntity()
        entity3 = SingleTypeEntityCollectionTestEntity()
        sut.add(entity1, entity2, entity3)
        assert [entity1, entity2, entity3] == list(sut)

    async def test___getitem___by_index(self) -> None:
        sut = SingleTypeEntityCollection[Entity](DummyEntity)
        entity1 = SingleTypeEntityCollectionTestEntity()
        entity2 = SingleTypeEntityCollectionTestEntity()
        entity3 = SingleTypeEntityCollectionTestEntity()
        sut.add(entity1, entity2, entity3)
        assert entity1 is sut[0]
        assert entity2 is sut[1]
        assert entity3 is sut[2]
        with pytest.raises(IndexError):
            sut[3]

    async def test___getitem___by_indices(self) -> None:
        sut = SingleTypeEntityCollection[Entity](DummyEntity)
        entity1 = SingleTypeEntityCollectionTestEntity()
        entity2 = SingleTypeEntityCollectionTestEntity()
        entity3 = SingleTypeEntityCollectionTestEntity()
        sut.add(entity1, entity2, entity3)
        assert [entity1, entity3] == list(sut[0::2])

    async def test___getitem___by_entity_id(self) -> None:
        sut = SingleTypeEntityCollection[Entity](DummyEntity)
        entity1 = SingleTypeEntityCollectionTestEntity("1")
        entity2 = SingleTypeEntityCollectionTestEntity("2")
        entity3 = SingleTypeEntityCollectionTestEntity("3")
        sut.add(entity1, entity2, entity3)
        assert entity1 is sut["1"]
        assert entity2 is sut["2"]
        assert entity3 is sut["3"]
        with pytest.raises(KeyError):
            sut["4"]

    async def test___delitem___by_entity(self) -> None:
        sut = SingleTypeEntityCollection[Entity](DummyEntity)
        entity1 = SingleTypeEntityCollectionTestEntity()
        entity2 = SingleTypeEntityCollectionTestEntity()
        entity3 = SingleTypeEntityCollectionTestEntity()
        sut.add(entity1, entity2, entity3)

        del sut[entity2]

        assert [entity1, entity3] == list(sut)

    async def test___delitem___by_entity_id(self) -> None:
        sut = SingleTypeEntityCollection[Entity](DummyEntity)
        entity1 = SingleTypeEntityCollectionTestEntity("1")
        entity2 = SingleTypeEntityCollectionTestEntity("2")
        entity3 = SingleTypeEntityCollectionTestEntity("3")
        sut.add(entity1, entity2, entity3)

        del sut["2"]

        assert [entity1, entity3] == list(sut)

    async def test___contains___by_entity(self) -> None:
        sut = SingleTypeEntityCollection[Entity](DummyEntity)
        entity1 = SingleTypeEntityCollectionTestEntity()
        entity2 = SingleTypeEntityCollectionTestEntity()
        sut.add(entity1)

        assert entity1 in sut
        assert entity2 not in sut

    async def test___contains___by_entity_id(self) -> None:
        sut = SingleTypeEntityCollection[Entity](DummyEntity)
        entity1 = SingleTypeEntityCollectionTestEntity()
        entity2 = SingleTypeEntityCollectionTestEntity()
        sut.add(entity1)

        assert entity1.id in sut
        assert entity2.id not in sut

    @pytest.mark.parametrize(
        "value",
        [
            True,
            False,
            [],
        ],
    )
    async def test___contains___by_unsupported_typed(self, value: Any) -> None:
        sut = SingleTypeEntityCollection[Entity](DummyEntity)
        entity = SingleTypeEntityCollectionTestEntity()
        sut.add(entity)

        assert value not in sut


class MultipleTypesEntityCollectionTestEntityOne(DummyEntity):
    pass


class MultipleTypesEntityCollectionTestEntityOther(DummyEntity):
    pass


class TestMultipleTypesEntityCollection:
    async def test_add(self) -> None:
        sut = MultipleTypesEntityCollection[Entity]()
        entity_one = MultipleTypesEntityCollectionTestEntityOne()
        entity_other1 = MultipleTypesEntityCollectionTestEntityOther()
        entity_other2 = MultipleTypesEntityCollectionTestEntityOther()
        entity_other3 = MultipleTypesEntityCollectionTestEntityOther()
        sut.add(entity_one, entity_other1, entity_other2, entity_other3)
        assert [entity_one] == list(sut[MultipleTypesEntityCollectionTestEntityOne])
        assert [entity_other1, entity_other2, entity_other3] == list(
            sut[MultipleTypesEntityCollectionTestEntityOther]
        )

    async def test_add_with_duplicate_entities(self) -> None:
        sut = MultipleTypesEntityCollection[Entity]()
        entity1 = MultipleTypesEntityCollectionTestEntityOne()
        entity2 = MultipleTypesEntityCollectionTestEntityOther()
        entity3 = MultipleTypesEntityCollectionTestEntityOne()
        entity4 = MultipleTypesEntityCollectionTestEntityOther()
        entity5 = MultipleTypesEntityCollectionTestEntityOne()
        entity6 = MultipleTypesEntityCollectionTestEntityOther()
        entity7 = MultipleTypesEntityCollectionTestEntityOne()
        entity8 = MultipleTypesEntityCollectionTestEntityOther()
        entity9 = MultipleTypesEntityCollectionTestEntityOne()
        # Ensure duplicates are skipped.
        sut.add(
            entity1,
            entity2,
            entity3,
            entity1,
            entity2,
            entity3,
            entity1,
            entity2,
            entity3,
        )
        assert [entity1, entity3] == list(
            sut[MultipleTypesEntityCollectionTestEntityOne]
        )
        assert [entity2] == list(sut[MultipleTypesEntityCollectionTestEntityOther])
        # Ensure skipped duplicates do not affect further new values.
        sut.add(
            entity1,
            entity2,
            entity3,
            entity4,
            entity5,
            entity6,
            entity7,
            entity8,
            entity9,
        )
        assert [entity1, entity3, entity5, entity7, entity9] == list(
            sut[MultipleTypesEntityCollectionTestEntityOne]
        )
        assert [entity2, entity4, entity6, entity8] == list(
            sut[MultipleTypesEntityCollectionTestEntityOther]
        )

    async def test_remove(self) -> None:
        sut = MultipleTypesEntityCollection[Entity]()
        entity_one = MultipleTypesEntityCollectionTestEntityOne()
        entity_other = MultipleTypesEntityCollectionTestEntityOther()
        sut[MultipleTypesEntityCollectionTestEntityOne].add(entity_one)
        sut[MultipleTypesEntityCollectionTestEntityOther].add(entity_other)
        sut.remove(entity_one)
        assert [entity_other] == list(sut)
        sut.remove(entity_other)
        assert list(sut) == []

    async def test___getitem___by_index(self) -> None:
        sut = MultipleTypesEntityCollection[Entity]()
        entity_one = MultipleTypesEntityCollectionTestEntityOne()
        entity_other = MultipleTypesEntityCollectionTestEntityOther()
        sut.add(entity_one, entity_other)
        assert entity_one is sut[0]
        assert entity_other is sut[1]
        with pytest.raises(IndexError):
            sut[2]

    async def test___getitem___by_indices(self) -> None:
        sut = MultipleTypesEntityCollection[Entity]()
        entity_one = MultipleTypesEntityCollectionTestEntityOne()
        entity_other = MultipleTypesEntityCollectionTestEntityOther()
        sut.add(entity_one, entity_other)
        assert [entity_one] == list(sut[0:1:1])
        assert [entity_other] == list(sut[1::1])

    async def test___getitem___by_entity_type(self) -> None:
        sut = MultipleTypesEntityCollection[Entity]()
        entity_one = MultipleTypesEntityCollectionTestEntityOne()
        entity_other = MultipleTypesEntityCollectionTestEntityOther()
        sut.add(entity_one, entity_other)
        assert [entity_one] == list(sut[MultipleTypesEntityCollectionTestEntityOne])
        assert [entity_other] == list(sut[MultipleTypesEntityCollectionTestEntityOther])
        # Ensure that getting previously unseen entity types automatically creates and returns a new collection.
        assert list(sut[DummyEntity]) == []

    async def test___getitem___by_entity_type_id(self) -> None:
        sut = MultipleTypesEntityCollection[Entity]()
        # Use an existing ancestry entity type, because converting an entity type name to an entity type only works for
        # entity types in a single module namespace.
        entity = Person()
        sut.add(entity)
        assert [entity] == list(sut["person"])
        # Ensure that getting previously unseen entity types automatically creates and returns a new collection.
        with pytest.raises(PluginNotFound):
            sut["NonExistentEntityType"]

    async def test___delitem___by_entity(self) -> None:
        sut = MultipleTypesEntityCollection[Entity]()
        entity1 = MultipleTypesEntityCollectionTestEntityOne()
        entity2 = MultipleTypesEntityCollectionTestEntityOne()
        entity3 = MultipleTypesEntityCollectionTestEntityOne()
        sut.add(entity1, entity2, entity3)

        del sut[entity2]

        assert [entity1, entity3] == list(sut)

    async def test___delitem___by_entity_type(self) -> None:
        sut = MultipleTypesEntityCollection[Entity]()
        entity = MultipleTypesEntityCollectionTestEntityOne()
        entity_other = MultipleTypesEntityCollectionTestEntityOther()
        sut.add(entity, entity_other)

        del sut[MultipleTypesEntityCollectionTestEntityOne]

        assert [entity_other] == list(sut)

    async def test___delitem___by_entity_type_id(self, mocker: MockerFixture) -> None:
        mocker.patch(
            "betty.model.ENTITY_TYPE_REPOSITORY",
            new=StaticPluginRepository(
                MultipleTypesEntityCollectionTestEntityOne,
                MultipleTypesEntityCollectionTestEntityOther,
            ),
        )
        sut = MultipleTypesEntityCollection[Entity]()
        entity = MultipleTypesEntityCollectionTestEntityOne()
        entity_other = MultipleTypesEntityCollectionTestEntityOther()
        sut.add(entity, entity_other)

        del sut[MultipleTypesEntityCollectionTestEntityOne.plugin_id()]

        assert [entity_other] == list(sut)

    async def test_iter(self) -> None:
        sut = MultipleTypesEntityCollection[Entity]()
        entity_one = MultipleTypesEntityCollectionTestEntityOne()
        entity_other = MultipleTypesEntityCollectionTestEntityOther()
        sut[MultipleTypesEntityCollectionTestEntityOne].add(entity_one)
        sut[MultipleTypesEntityCollectionTestEntityOther].add(entity_other)
        assert [entity_one, entity_other] == list(sut)

    async def test_len(self) -> None:
        sut = MultipleTypesEntityCollection[Entity]()
        entity_one = MultipleTypesEntityCollectionTestEntityOne()
        entity_other = MultipleTypesEntityCollectionTestEntityOther()
        sut[MultipleTypesEntityCollectionTestEntityOne].add(entity_one)
        sut[MultipleTypesEntityCollectionTestEntityOther].add(entity_other)
        assert len(sut) == 2

    async def test_contain_by_entity(self) -> None:
        sut = MultipleTypesEntityCollection[Entity]()
        entity_one = MultipleTypesEntityCollectionTestEntityOne()
        entity_other1 = MultipleTypesEntityCollectionTestEntityOther()
        entity_other2 = MultipleTypesEntityCollectionTestEntityOther()
        sut[MultipleTypesEntityCollectionTestEntityOne].add(entity_one)
        sut[MultipleTypesEntityCollectionTestEntityOther].add(entity_other1)
        assert entity_one in sut
        assert entity_other1 in sut
        assert entity_other2 not in sut

    @pytest.mark.parametrize(
        "value",
        [
            True,
            False,
            [],
        ],
    )
    async def test___contains___by_unsupported_type(self, value: Any) -> None:
        sut = MultipleTypesEntityCollection[Entity]()
        entity = MultipleTypesEntityCollectionTestEntityOne()
        sut.add(entity)

        assert value not in sut