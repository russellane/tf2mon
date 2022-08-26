"""Module importer."""

from __future__ import annotations

import importlib

# import logging
import pkgutil


class Importer:
    """Module importer."""

    def __init__(
        self,
        modname: str,
        basename: str = None,
        prefix: str = None,
        suffix: str = None,
    ) -> None:
        """Import all modules in `modname` and instantiate all classes therein.

        foreach MODULE in containing module `modname`:
            foreach CLASS in MODULE:
                OBJ = CLASS()
                cache[CLASS.name] = OBJ

        1. Load each module in containing module `modname`,
        2. Instantiate an instance of each module's class, and
        3. Cache the object for subsequent retrieval by its classname.

        If all classes are not named by `basename`, then they must all
        begin and/or end with a common tag. Pass `prefix` and/or `suffix` to
        specify, and the longest matching class will be used. Multiple
        command classes could be defined in one module this way.


        e.g.,
            app/app.py:
                imp = ModuleImporter("app.controls", baseclass="Control")

            tests/apps/common/controls/__init__.py:
                class BaseControl:

            tests/apps/common/controls/volume.py:
                class Control(BaseControl):

        """

        self.classes: dict[str, object] = {}

        # logging.debug("modname=`%s`", modname)

        modpath = importlib.import_module(modname, __name__).__path__
        # logging.debug("modpath=`%s`", modpath)

        super_name = (prefix or "") + (suffix or "")
        # logging.debug("super_name=`%s`", super_name)

        for modinfo in pkgutil.iter_modules(modpath):
            # logging.debug("modinfo=`%s`", modinfo)

            module = importlib.import_module(f"{modname}.{modinfo.name}", __name__)
            # logging.debug("module=`%s`", module)

            if not prefix and not suffix and (klass := getattr(module, basename, None)):
                self.classes[modinfo.name] = klass
                continue

            # for name in [x for x in dir(module) if x != super_name]:
            for name in dir(module):
                # logging.debug("NAME=`%s`", name)
                if name == super_name:
                    # logging.error("super_name")
                    continue
                if prefix and not name.startswith(prefix):
                    continue
                if suffix and not name.endswith(suffix):
                    continue
                if (klass := getattr(module, name, None)) is not None:
                    self.classes[name] = klass

    def __repr__(self) -> str:
        """Represent."""

        classes = ", ".join(self.classes)
        return f"{self.__class__.__name__}({classes})"

    def __getitem__(self, name: str):
        """Return the class known as `name`."""

        return self.classes[name]
