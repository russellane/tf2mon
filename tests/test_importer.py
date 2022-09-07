from tf2mon.importer import Importer

_debug = False


def test_basename():
    """Test app with all handler classes named `Control`; limit 1 class per file."""
    if _debug:
        print("Begin test")
    importer = Importer("tests.apps.common.controls", basename="Control")
    if _debug:
        print(importer)
    assert repr(importer) == "Importer(brightness, volume)"


def test_prefix():
    """Test app with all handler classnames prefixed with `Television`."""
    if _debug:
        print("Begin test")
    importer = Importer("tests.apps.prefix.controls", prefix="Television")
    if _debug:
        print(importer)
    assert repr(importer) == "Importer(TelevisionBrightness, TelevisionVolume)"


def test_suffix():
    """Test app with all handler classnames suffixed with `Control`."""
    if _debug:
        print("Begin test")
    importer = Importer("tests.apps.suffix.controls", suffix="Control")
    if _debug:
        print(importer)
    assert repr(importer) == "Importer(BrightnessControl, VolumeControl)"


def test_both():
    """Test app with all handler classnames prefixed with `Television` and suffixed with `Control`."""  # noqa
    if _debug:
        print("Begin test")
    importer = Importer("tests.apps.both.controls", prefix="Television", suffix="Control")
    if _debug:
        print(importer)
    assert repr(importer) == "Importer(TelevisionBrightnessControl, TelevisionVolumeControl)"
