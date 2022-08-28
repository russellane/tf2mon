"""Module importer."""

import importlib
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
        """Import all modules in `modname`.

        Cache the object for subsequent retrieval by its classname.

        If all classes are not named by `basename`, then they must all
        begin and/or end with a common tag. Pass `prefix` and/or `suffix` to
        specify, and the longest matching class will be used. Multiple
        command classes could be defined in one module this way.
        """

        self.classes: dict[str, type] = {}

        modpath = importlib.import_module(modname, __name__).__path__
        super_name = (prefix or "") + (suffix or "")

        for modinfo in pkgutil.iter_modules(modpath):

            module = importlib.import_module(f"{modname}.{modinfo.name}", __name__)

            if not prefix and not suffix and (klass := getattr(module, basename, None)):
                self.classes[modinfo.name] = klass
                continue

            for name in [x for x in dir(module) if x != super_name]:
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
