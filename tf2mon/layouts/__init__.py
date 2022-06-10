"""Grid layouts."""

from enum import Enum

from tf2mon.layouts.default import DefaultLayout
from tf2mon.layouts.full import FullLayout
from tf2mon.layouts.tall import TallLayout
from tf2mon.layouts.wide import WideLayout

GRID_LAYOUT = Enum("_grid_layout_enum", "DFLT FULL TALL WIDE")
GRID_LAYOUT.__doc__ = "Grid layout."

GRID_LAYOUT_CLASSES = {
    GRID_LAYOUT.DFLT: DefaultLayout,
    GRID_LAYOUT.FULL: FullLayout,
    GRID_LAYOUT.TALL: TallLayout,
    GRID_LAYOUT.WIDE: WideLayout,
}

# import importlib
# import pkgutil
# from icecream import ic
# from loguru import logger
#
# def load_layouts() -> None:
#   """Load all layouts in `tf2mon.layouts`."""
#
#   global GRID_LAYOUT  # noqa
#   global GRID_LAYOUT_CLASSES  # noqa
#
#   modname = "tf2mon.layouts"
#   layouts_module_path = importlib.import_module(modname, __name__).__path__
#
#   classes_by_name = {}
#
#   for modinfo in pkgutil.iter_modules(layouts_module_path):
#       logger.debug(f"importing {modname}.{modinfo.name}")
#       module = importlib.import_module(f"{modname}.{modinfo.name}", __name__)
#
#       for name in [x for x in dir(module) if x != "BaseLayout" and x.endswith("Layout")]:
#           klass = getattr(module, name)
#           _name = name[:-6]  # rstrip("Layout")
#           classes_by_name[_name] = klass
#
#   GRID_LAYOUT = Enum("_grid_layout_enum", " ".join(classes_by_name.keys()))
#   GRID_LAYOUT.__doc__ = "Grid layout."
#   GRID_LAYOUT_CLASSES = {x: classes_by_name[x.name] for x in list(GRID_LAYOUT)}
