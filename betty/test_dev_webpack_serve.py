# @todo REMOVE THIS FILE
from pathlib import Path

from typing_extensions import override

from betty.project import Project
from betty.project.extension.webpack.build import BuildWatchIntegrator


# @todo Finish this
class Integrator(BuildWatchIntegrator):
    @override
    def watch_files(self) -> set[Path]:
        return {Path(__file__).parent / "data"}

    @override
    async def setup(self, project: Project) -> None:
        # @todo Finish this
        raise NotImplementedError
