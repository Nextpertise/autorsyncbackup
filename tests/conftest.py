import pytest

from lib.jinjafilters import jinjafilters


@pytest.fixture
def filters():
    filters = jinjafilters()

    yield filters
