from fontrefinery.fixes import FixResult, fix
from fontrefinery.testable import Font


@fix("com.google.fonts/check/dsig")
def fix_dsig(font: Font, _context) -> FixResult:
    if "DSIG" in font.ttFont:
        del font.ttFont["DSIG"]
        return True, ["Removed DSIG table"]
    return False, []
