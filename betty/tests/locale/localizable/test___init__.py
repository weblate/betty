from collections.abc import Sequence
from gettext import NullTranslations

import pytest
from typing_extensions import override

from betty.json.schema import Schema
from betty.locale import DEFAULT_LOCALE, UNDETERMINED_LOCALE
from betty.locale.localizable import (
    StaticTranslationsLocalizable,
    plain,
    StaticTranslations,
    StaticTranslationsLocalizableSchema,
    join,
    do_you_mean,
    Localizable,
    RequiredStaticTranslationsLocalizableAttr,
    OptionalStaticTranslationsLocalizableAttr,
)
from betty.locale.localizable import (
    static,
    ShorthandStaticTranslations,
)
from betty.locale.localizer import Localizer, DEFAULT_LOCALIZER
from betty.serde.dump import Dump, DumpMapping
from betty.test_utils.json.linked_data import assert_dumps_linked_data
from betty.test_utils.json.schema import SchemaTestBase


class TestStaticTranslationsLocalizable:
    @pytest.mark.parametrize(
        ("expected", "locale", "translations"),
        [
            # A translation in an undetermined locale.
            (
                "Hello, world!",
                "en-US",
                "Hello, world!",
            ),
            # An exact locale match.
            (
                "Hello, world!",
                "en-US",
                {
                    "en-US": "Hello, world!",
                },
            ),
            # A negotiated locale match.
            (
                "Hello, world!",
                "en-US",
                {
                    "nl-NL": "Hallo, wereld!",
                    "en": "Hello, world!",
                },
            ),
            # No locale match, expect the fallback.
            (
                "Hello, world!",
                "de-DE",
                {
                    "en": "Hello, world!",
                    "nl-NL": "Hallo, wereld!",
                },
            ),
        ],
    )
    async def test_localize_with_translations(
        self, expected: str, locale: str, translations: ShorthandStaticTranslations
    ) -> None:
        sut = StaticTranslationsLocalizable(translations)
        localizer = Localizer(locale, NullTranslations())
        assert sut.localize(localizer) == expected

    def test___getitem__(self) -> None:
        locale = "nl-NL"
        translation = "Hallo, wereld!"
        sut = StaticTranslationsLocalizable(
            {
                DEFAULT_LOCALE: "Hello, world!",
                locale: translation,
            }
        )
        assert sut[locale] == translation

    def test___setitem__(self) -> None:
        locale = "nl-NL"
        translation = "Hallo, wereld!"
        sut = StaticTranslationsLocalizable({DEFAULT_LOCALE: "Hello, world!"})
        sut[locale] = translation
        assert sut[locale] == translation

    @pytest.mark.parametrize(
        ("expected", "translations"),
        [
            (
                0,
                {},
            ),
            (
                1,
                "Hello, world!",
            ),
            (
                1,
                {
                    "en-US": "Hello, world!",
                },
            ),
            (
                2,
                {
                    "nl-NL": "Hallo, wereld!",
                    "en": "Hello, world!",
                },
            ),
        ],
    )
    async def test___len__(
        self, expected: int, translations: ShorthandStaticTranslations
    ) -> None:
        sut = StaticTranslationsLocalizable(translations, required=False)
        assert len(sut) == expected

    @pytest.mark.parametrize(
        ("expected", "translations"),
        [
            (
                {},
                {},
            ),
            (
                {UNDETERMINED_LOCALE: "Hello, world!"},
                "Hello, world!",
            ),
            (
                {
                    "en-US": "Hello, world!",
                },
                {
                    "en-US": "Hello, world!",
                },
            ),
            (
                {
                    "nl-NL": "Hallo, wereld!",
                    "en": "Hello, world!",
                },
                {
                    "nl-NL": "Hallo, wereld!",
                    "en": "Hello, world!",
                },
            ),
        ],
    )
    async def test_translations(
        self, expected: StaticTranslations, translations: ShorthandStaticTranslations
    ) -> None:
        sut = StaticTranslationsLocalizable(translations, required=False)
        assert sut.translations == expected

    def test_replace(self) -> None:
        translation = "Hallo, wereld!"
        sut = StaticTranslationsLocalizable(required=False)
        sut.replace(translation)
        assert sut.localize(DEFAULT_LOCALIZER) == translation

    @pytest.mark.parametrize(
        ("expected", "translations"),
        [
            (
                {},
                {},
            ),
            (
                {UNDETERMINED_LOCALE: "Hello, world!"},
                "Hello, world!",
            ),
            (
                {"en-US": "Hello, world!"},
                {
                    "en-US": "Hello, world!",
                },
            ),
            (
                {"nl-NL": "Hallo, wereld!", "en": "Hello, world!"},
                {
                    "nl-NL": "Hallo, wereld!",
                    "en": "Hello, world!",
                },
            ),
        ],
    )
    async def test_dump_linked_data(
        self,
        expected: DumpMapping[Dump],
        translations: ShorthandStaticTranslations,
    ) -> None:
        sut = StaticTranslationsLocalizable(translations, required=False)
        actual = await assert_dumps_linked_data(sut)
        assert actual == expected


class TestStaticTranslationsLocalizableSchema(SchemaTestBase):
    @override
    async def get_sut_instances(
        self,
    ) -> Sequence[tuple[Schema, Sequence[Dump], Sequence[Dump]]]:
        valid_datas: Sequence[Dump] = [
            {DEFAULT_LOCALE: "Hello, world!"},
            {"nl": "Hallo, wereld!", "uk": "Привіт Світ!"},
        ]
        invalid_datas: Sequence[Dump] = [
            True,
            False,
            None,
            123,
            [],
            {DEFAULT_LOCALE: True},
            {DEFAULT_LOCALE: False},
            {DEFAULT_LOCALE: None},
            {DEFAULT_LOCALE: 123},
            {DEFAULT_LOCALE: []},
            {DEFAULT_LOCALE: {}},
        ]
        return [
            (
                StaticTranslationsLocalizableSchema(),
                valid_datas,
                invalid_datas,
            ),
        ]


class TestRequiredStaticTranslationsLocalizableAttr:
    class Instance:
        attr = RequiredStaticTranslationsLocalizableAttr("attr")

    def test___get__(self) -> None:
        instance = self.Instance()
        instance.attr  # noqa B018

    def test___set__(self) -> None:
        translation = "Hello, world!"
        instance = self.Instance()
        instance.attr = translation
        assert instance.attr[UNDETERMINED_LOCALE] == translation


class TestOptionalStaticTranslationsLocalizableAttr:
    class Instance:
        attr = OptionalStaticTranslationsLocalizableAttr("attr")

    def test___get__(self) -> None:
        instance = self.Instance()
        instance.attr  # noqa B018

    def test___set__(self) -> None:
        translation = "Hello, world!"
        instance = self.Instance()
        instance.attr = translation
        assert instance.attr[UNDETERMINED_LOCALE] == translation

    def test___delete__(self) -> None:
        translation = "Hello, world!"
        instance = self.Instance()
        instance.attr = translation
        del instance.attr
        with pytest.raises(KeyError):
            instance.attr[UNDETERMINED_LOCALE]  # noqa B018


class TestStatic:
    @pytest.mark.parametrize(
        "translations",
        [
            "Hello, world!",
            {
                "en-US": "Hello, world!",
                "nl-NL": "Hallo, wereld!",
            },
        ],
    )
    async def test(self, translations: ShorthandStaticTranslations) -> None:
        static(translations)


class TestPlain:
    @pytest.mark.parametrize(
        "string",
        [
            "Hello, world!",
            "Hallo, wereld!",
        ],
    )
    async def test(self, string: str) -> None:
        assert plain(string).localize(DEFAULT_LOCALIZER) == string


class TestJoin:
    @pytest.mark.parametrize(
        ("expected", "localizables"),
        [
            ("", []),
            ("foo", [plain("foo")]),
            ("foo bar baz", [plain("foo"), plain("bar"), plain("baz")]),
        ],
    )
    async def test(self, expected: str, localizables: Sequence[Localizable]) -> None:
        assert join(*localizables).localize(DEFAULT_LOCALIZER) == expected


class TestDoYouMean:
    @pytest.mark.parametrize(
        ("expected", "available_options"),
        [
            ("There are no available options.", []),
            ("Do you mean foo?", ["foo"]),
            ("Do you mean one of bar, baz, foo?", ["foo", "bar", "baz"]),
        ],
    )
    async def test(self, expected: str, available_options: Sequence[str]) -> None:
        assert do_you_mean(*available_options).localize(DEFAULT_LOCALIZER) == expected
