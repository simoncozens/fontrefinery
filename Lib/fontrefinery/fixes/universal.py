from fontbakery.checks.universal.metrics import vmetrics
from fontrefinery.fixes import fix, FixResult


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
