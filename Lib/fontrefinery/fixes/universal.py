from fontbakery.checks.universal.metrics import vmetrics
from fontbakery.utils import get_glyph_name

from fontrefinery.fixes import FixResult, fix


@fix(id="com.google.fonts/check/family/win_ascent_and_descent")
def fix_family_win_ascent_and_descent(font, context) -> FixResult:
    """Fixes the winAscent and winDescent values in the OS/2 table."""
    os2_table = font.ttFont["OS/2"]
    win_ascent = os2_table.usWinAscent
    win_descent = os2_table.usWinDescent
    y_max = context.vmetrics["ymax"]
    y_min = context.vmetrics["ymin"]
    changed = False
    messages = []
    if win_ascent < y_max or win_ascent > y_max * 2:
        os2_table.usWinAscent = y_max
        changed = True
        messages.append(f"winAscent changed from {win_ascent} to {y_max}")
    if win_descent < abs(y_min) or win_descent > abs(y_min) * 2:
        os2_table.usWinDescent = abs(y_min)
        changed = True
        messages.append(f"winDescent changed from {win_descent} to {abs(y_min)}")
    return changed, messages


@fix(id="com.google.fonts/check/name/trailing_spaces")
def fix_name_trailing_spaces(font, context) -> FixResult:
    messages = []
    for i, nameRecord in enumerate(font.ttFont["name"].names):
        name_string = nameRecord.toUnicode()
        if name_string != name_string.strip():
            nameRecord.string = name_string.strip().encode(nameRecord.getEncoding())
            messages.append(f"Removed trailing spaces from nameID {nameRecord.nameID}")
    if messages:
        return True, messages
    return False, []


@fix(id="com.google.fonts/check/soft_hyphen")
def fix_soft_hyphen(font, context) -> FixResult:
    messages = []
    for cmap in font.ttFont["cmap"].tables:
        if 0x00AD in cmap.cmap:
            del cmap.cmap[0x00AD]
            messages.append(f"Removed soft hyphen from cmap subtable {cmap.format}")
    if messages:
        return True, messages
    return False, []


@fix(id="com.google.fonts/check/whitespace_widths")
def fix_whitespace_widths(font, context) -> FixResult:
    # This won't work on variable fonts but anyway it silences the WARN, so?
    space_name = get_glyph_name(font.ttFont, 0x0020)
    nbsp_name = get_glyph_name(font.ttFont, 0x00A0)
    if (
        space_name
        and nbsp_name
        and font.ttFont["hmtx"][space_name][0] != font.ttFont["hmtx"][nbsp_name][0]
    ):
        font.ttFont["hmtx"][nbsp_name] = (
            font.ttFont["hmtx"][space_name][0],
            font.ttFont["hmtx"][nbsp_name][1],
        )
        return True, [
            f"Set width of {nbsp_name} to {font.ttFont['hmtx'][space_name][0]}"
        ]
    return False, []
