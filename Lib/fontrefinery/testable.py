from dataclasses import dataclass

from fontbakery.testable import Font as FBFont
from fontbakery.testable import CheckRunContext
from fontTools.ttLib import TTFont


@dataclass
class Font(FBFont):
    def __post_init__(self):
        self._ttFont = TTFont(self.file)

    @property
    def ttFont(self):
        return self._ttFont

    @ttFont.setter
    def ttFont(self, value):
        self._ttFont = value


class FixContext(CheckRunContext):
    def __init__(self, fonts):
        super().__init__(fonts)
        # self.fonts = fonts
