import io
import logging
from asyncio import to_thread
from collections.abc import AsyncIterator
from logging import CRITICAL, ERROR, WARNING, INFO, DEBUG, FATAL, WARN, NOTSET
from typing import Any, IO

import pytest
from betty.app import App
from betty.cli import main, _ClickHandler
from betty.cli.commands import command, Command
from betty.config import write_configuration_file
from betty.locale.localizer import DEFAULT_LOCALIZER
from betty.plugin.static import StaticPluginRepository
from betty.project import Project
from betty.serve import Server, ProjectServer
from click.testing import CliRunner, Result
from pytest_mock import MockerFixture
from typing_extensions import override


@command(name="no-op")
async def _no_op_command() -> None:
    pass


class _NoOpCommand(Command):
    _click_command = _no_op_command


def run(
    *args: str,
    expected_exit_code: int = 0,
    input: str | bytes | IO[Any] | None = None,  # noqa A002
) -> Result:
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(main, args, catch_exceptions=False, input=input)
    if result.exit_code != expected_exit_code:
        raise AssertionError(
            f"""
The Betty command `{" ".join(args)}` unexpectedly exited with code {result.exit_code}, but {expected_exit_code} was expected.
Stdout:
{result.stdout}
Stderr:
{result.stderr}
"""
        )
    return result


@pytest.fixture()
async def new_temporary_app(mocker: MockerFixture) -> AsyncIterator[App]:
    async with App.new_temporary() as app:
        m_new_from_environment = mocker.AsyncMock()
        m_new_from_environment.__aenter__.return_value = app
        mocker.patch(
            "betty.app.App.new_from_environment", return_value=m_new_from_environment
        )
        yield app


class TestMain:
    async def test_without_arguments(self, new_temporary_app: App) -> None:
        await to_thread(run)

    async def test_help(self, new_temporary_app: App) -> None:
        await to_thread(run, "--help")


class TestVersion:
    async def test(self, new_temporary_app: App) -> None:
        result = run("--version")
        assert "Betty" in result.stdout


class TestClearCaches:
    async def test(self, new_temporary_app: App) -> None:
        async with new_temporary_app:
            await new_temporary_app.cache.set("KeepMeAroundPlease", "")
        await to_thread(run, "clear-caches")
        async with new_temporary_app, new_temporary_app.cache.get(
            "KeepMeAroundPlease"
        ) as cache_item:
            assert cache_item is None


class NoOpServer(Server):
    def __init__(self, *_: Any, **__: Any):
        Server.__init__(self, DEFAULT_LOCALIZER)

    @override
    @property
    def public_url(self) -> str:
        return "https://example.com"

    @override
    async def start(self) -> None:
        pass

    @override
    async def stop(self) -> None:
        pass

    @override
    async def show(self) -> None:
        pass


class NoOpProjectServer(NoOpServer, ProjectServer):
    pass


class TestUnknownCommand:
    async def test(self) -> None:
        await to_thread(run, "unknown-command", expected_exit_code=2)


class TestVerbosity:
    @pytest.mark.parametrize(
        "verbosity",
        [
            "-v",
            "-vv",
            "-vvv",
        ],
    )
    async def test(
        self, mocker: MockerFixture, new_temporary_app: App, verbosity: str
    ) -> None:
        command_repository = StaticPluginRepository(_NoOpCommand)
        mocker.patch(
            "betty.cli.commands.COMMAND_REPOSITORY",
            new=command_repository,
        )
        async with Project.new_temporary(new_temporary_app) as project:
            await write_configuration_file(
                project.configuration, project.configuration.configuration_file_path
            )
            await to_thread(run, "no-op", verbosity)


class TestClickHandler:
    @pytest.mark.parametrize(
        "level",
        [
            CRITICAL,
            FATAL,
            ERROR,
            WARNING,
            WARN,
            INFO,
            DEBUG,
            NOTSET,
        ],
    )
    async def test_emit(self, level: int) -> None:
        stream = io.StringIO()
        sut = _ClickHandler(stream)
        sut.emit(
            logging.LogRecord(
                __name__, level, __file__, 0, "Something went wrong!", (), None
            )
        )
        assert stream.getvalue() == "Something went wrong!\n"
