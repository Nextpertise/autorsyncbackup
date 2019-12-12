from _version import __version__
from autorsyncbackup import (
    setupCliArguments,
    getVersion,
)


def test_setupCliArguments():
    options = setupCliArguments()

    assert options.mainconfig == '/etc/autorsyncbackup/main.yaml'
    assert options.dryrun is False
    assert options.verbose is False
    assert options.version is False
    assert options.job is None
    assert options.sort is None
    assert options.hostname is None


def test_getVersion():
    assert getVersion() == __version__
