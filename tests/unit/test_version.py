import mixedtape


def test_version_exposed():
    assert isinstance(mixedtape.__version__, str)
    assert mixedtape.__version__
