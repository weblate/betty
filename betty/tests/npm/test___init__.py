from subprocess import CalledProcessError

import pytest

from betty.app import App
from betty.npm import _NpmRequirement


class TestNpmRequirement:
    def test_check_met(self) -> None:
        with App():
            sut = _NpmRequirement.check()
        assert sut.met

    @pytest.mark.parametrize('e', [
        CalledProcessError(1, ''),
        FileNotFoundError(),
    ])
    def test_check_unmet(self, e: Exception, mocker) -> None:
        m_npm = mocker.patch('betty.npm.npm')
        m_npm.side_effect = e
        with App():
            sut = _NpmRequirement.check()
        assert not sut.met
