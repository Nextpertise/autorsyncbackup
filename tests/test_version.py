import re

from _version import __version__


def test_version():
    assert __version__ is not None
    assert re.match(r'^\d+\.\d+\.\d+(a|b|dev)?$', __version__)
