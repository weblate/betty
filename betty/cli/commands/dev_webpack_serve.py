from __future__ import annotations  # noqa D100

import logging
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING, final, Self

import asyncclick as click
from typing_extensions import override

from betty.app.factory import AppDependentFactory
from betty.cli.commands import command, Command, parameter_callback
from betty.importlib import import_any
from betty.locale.localizable import _
from betty.plugin import ShorthandPluginBase
from betty.project import Project
from betty.project.extension.webpack.build import Builder, BuildWatchIntegrator

if TYPE_CHECKING:
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

        def _integrator_callback(_: click.Context, __: click.Parameter, name: str) -> BuildWatchIntegrator:
            try:
                integrator = import_any(name)
            except ImportError as error:
                raise click.BadParameter(str(error)) from error
            if not issubclass(integrator, BuildWatchIntegrator):
                raise click.BadParameter(f"{integrator} must extend {BuildWatchIntegrator}, but does not.")
            return integrator(self._app)

        @command(
            self.plugin_id(),
            short_help=self.plugin_label().localize(localizer),
            help=description.localize(localizer)
            if description
            else self.plugin_label().localize(localizer),
        )
        @click.argument(
            "integrator",
            required=True,
            callback=_integrator_callback
        )
        async def dev_webpack_serve(integrator: BuildWatchIntegrator) -> None:
            # @todo Do we use these directories?
            with (
                TemporaryDirectory() as project_directory_path_str,
                TemporaryDirectory(),
            ):
                # @todo Ensure that the Webpack build copies the files to the desired destination itself.
                # @todo We currently do this in Python, which is fine because we can reliably do this after the
                # @todo single Webpack build. With live builds, however, the Webpack process has control and there
                # @todo is no Python step after a rebuild.
                # @todo ACTUALLY!!!! The reason we do it in Python is that the Webpack builds are cacheable, meaning
                # @todo that during normal operations Webpack isn't invoked at all, but instead Python just copies the
                # @todo necessary (previously built) files from the cache to the project output directory.
                # @todo
                project_directory_path = Path(project_directory_path_str)
                async with Project.new() as project:
                    await integrator.setup(project)
                    async with project:
                        builder = Builder(
                            project_directory_path, [], False, await self._app.renderer
                        )
                        await builder.build_watch(integrator)
                        raise NotImplementedError

        return dev_webpack_serve
