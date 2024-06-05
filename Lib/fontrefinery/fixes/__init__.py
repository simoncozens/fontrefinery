import inspect
import importlib
import pkgutil
import warnings
import sys
from typing import Union, List, Tuple, Any

from fontTools.ttLib import TTFont
from fontbakery.callable import FontbakeryCallable


FixResult = Tuple[bool, List[str]]


def expect_field(
    ttFont: TTFont, table: str, field: str, value: Any, getter=None, setter=None
) -> FixResult:
    """Check that a table has a field with the expected value"""
    if getter is not None:
        previous = getter(ttFont)
    else:
        previous = getattr(ttFont[table], field)
    if previous == value:
        return False, []
    if setter is not None:
        setter(ttFont, value)
    else:
        setattr(ttFont[table], field, value)
    return True, [f"Set {table}.{field} to {value} (was {previous})"]


class FontRefineryFix(FontbakeryCallable):
    def __init__(self, checkfunc, id: Union[str, List[str]], **kwds):
        super().__init__(checkfunc)
        if isinstance(id, str):
            id = [id]
        self.id = id
        # self.description = description


def fix(*args, **kwds):
    """Check wrapper, a factory for FontBakeryCheck

    Requires all arguments of FontBakeryCheck but not `checkfunc`
    which is passed via the decorator syntax.
    """

    def wrapper(checkfunc):
        return FontRefineryFix(checkfunc, *args, **kwds)

    return wrapper


class FixDirectory:
    __all_fixes = {}

    def __init__(self):
        self.__dict__ = self.__all_fixes
        if not self.__all_fixes:
            self.load_all_fixes()

    def __getitem__(self, key):
        return self.__all_fixes[key]

    def load_all_fixes(self, package=sys.modules[__name__]):
        for _, import_path, _ in pkgutil.walk_packages(
            path=package.__path__, prefix=package.__name__ + "."
        ):
            try:
                module = importlib.import_module(import_path)
            except ImportError as e:
                warnings.warn("Failed to load %s: %s" % (import_path, e))
                continue
            self.load_fixes_from_module(module)

    def load_fixes_from_module(self, module):
        for _name, definition in inspect.getmembers(module):
            if isinstance(definition, FontRefineryFix):
                for fix_id in definition.id:
                    self.__all_fixes[fix_id] = definition
