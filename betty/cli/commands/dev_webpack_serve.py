from __future__ import annotations  # noqa D100

from typing import TYPE_CHECKING, final, Self

from typing_extensions import override

from betty.app.factory import AppDependentFactory
from betty.cli.commands import command, Command
from betty.locale.localizable import _
from betty.plugin import ShorthandPluginBase

if TYPE_CHECKING:
    import asyncclick as click
    from betty.app import App


@final
class DevWebpackServe(ShorthandPluginBase, AppDependentFactory, Command):
    """
    A command to run a live Webpack build and serve the result.
    """

    _plugin_id = "dev-webpack-serve"
    _plugin_label = _("Run a live Webpack build and serve the result")

    def __init__(self, app: App):
        self._app = app

    @override
    @classmethod
    async def new_for_app(cls, app: App) -> Self:
        return cls(app)

    @override
    async def click_command(self) -> click.Command:
        localizer = await self._app.localizer
        description = self.plugin_description()

        @command(
            self.plugin_id(),
            short_help=self.plugin_label().localize(localizer),
            help=description.localize(localizer)
            if description
            else self.plugin_label().localize(localizer),
        )
        async def dev_webpack_serve() -> None:
            raise NotImplementedError

        return dev_webpack_serve
