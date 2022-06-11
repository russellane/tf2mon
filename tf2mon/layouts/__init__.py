"""Grid layouts."""

from enum import Enum

from tf2mon.layouts.default import DefaultLayout
from tf2mon.layouts.full import FullLayout
from tf2mon.layouts.tall import TallLayout
from tf2mon.layouts.wide import WideLayout

LAYOUT_ENUM = Enum("_layout_enum", "DFLT FULL TALL WIDE")
LAYOUT_ENUM.__doc__ = "Grid layout."

LAYOUT_CLASSES = {
    LAYOUT_ENUM.DFLT: DefaultLayout,
    LAYOUT_ENUM.FULL: FullLayout,
    LAYOUT_ENUM.TALL: TallLayout,
    LAYOUT_ENUM.WIDE: WideLayout,
}
