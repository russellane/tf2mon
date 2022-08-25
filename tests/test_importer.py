from tf2mon.importer import Importer

# import logging
# import pytest
# logging.basicConfig(force=True, level=logging.DEBUG)


def test_basename():
    """Test app with all handler classes named `Control`; limit 1 class per file."""
    # logging.debug("Begin test")
    importer = Importer("tests.apps.common.controls", basename="Control")
    # logging.debug(importer)
    assert repr(importer) == "Importer(brightness, volume)"


def test_prefix():
    """Test app with all handler classnames prefixed with `Television`."""
    # logging.debug("Begin test")
    importer = Importer("tests.apps.prefix.controls", prefix="Television")
    # logging.debug(importer)
    assert repr(importer) == "Importer(TelevisionBrightness, TelevisionVolume)"


def test_suffix():
    """Test app with all handler classnames suffixed with `Control`."""
    # logging.debug("Begin test")
    importer = Importer("tests.apps.suffix.controls", suffix="Control")
    # logging.debug(importer)
    assert repr(importer) == "Importer(BrightnessControl, VolumeControl)"


def test_both():
    """Test app with all handler classnames prefixed with `Television` and suffixed with `Control`."""  # noqa
    # logging.debug("Begin test")
    importer = Importer("tests.apps.both.controls", prefix="Television", suffix="Control")
    # logging.debug(importer)
    assert repr(importer) == "Importer(TelevisionBrightnessControl, TelevisionVolumeControl)"
