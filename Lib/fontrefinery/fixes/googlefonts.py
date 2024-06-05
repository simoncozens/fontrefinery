import re

from fontbakery.checks.googlefonts.conditions import family_metadata, font_metadata
from fontbakery.checks.googlefonts.constants import EXPECTED_COPYRIGHT_PATTERN
from fontbakery.checks.googlefonts.license import license_contents, license_path
from fontbakery.constants import NameID
from fontTools.misc.timeTools import timestampToString
from gftools.fix import fix_ofl_license
from gftools.utils import font_stylename
from gftools.util.google_fonts import WriteMetadata

from fontrefinery.testable import Font
from fontrefinery.fixes import FixResult, expect_field, fix


@fix("com.google.fonts/check/fstype")
def fix_fs_type(font: Font, _context) -> FixResult:
    """Set the OS/2 table's fsType flag to 0 (Installable embedding)."""
    return expect_field(font.ttFont, "OS/2", "fsType", 0)


@fix(
    [
        "com.google.fonts/check/os2/use_typo_metrics",
        "com.google.fonts/check/fsselection",
    ]
)
def fix_fs_selection(font: Font) -> FixResult:
    """Fix the OS/2 table's fsSelection so it conforms to GF's supported
    styles table:
    https://github.com/googlefonts/gf-docs/tree/main/Spec#supported-styles
    """
    ttFont = font.ttFont
    stylename = font_stylename(ttFont)
    tokens = set(stylename.split())
    fs_selection = ttFont["OS/2"].fsSelection

    # turn off all bits except for bit 7 (USE_TYPO_METRICS)
    fs_selection &= 1 << 7

    if "Italic" in tokens:
        fs_selection |= 1 << 0
    if "Bold" in tokens:
        fs_selection |= 1 << 5
    # enable Regular bit for all other styles
    if not tokens & set(["Bold", "Italic"]):
        fs_selection |= 1 << 6
    return expect_field(ttFont, "OS/2", "fsSelection", fs_selection)


@fix(
    id=[
        "com.google.fonts/check/font_copyright",
        "com.google.fonts/check/license/OFL_copyright",
    ]
)
def fix_font_copyright(font, _context) -> FixResult:
    if not font.family_metadata:
        return False, ["Metadata is missing"]
    if not font.family_metadata.source.repository_url:
        return False, ["Repository URL is missing in METADATA.pb"]

    font_year = timestampToString(font.ttFont["head"].created)[-4:]
    expected_copyright = f"Copyright {font_year}, the {font.family_metadata.name} Project Authors ({font.family_metadata.source.repository_url})"
    messages = []
    font_changed = False
    if not re.match(EXPECTED_COPYRIGHT_PATTERN, font.font_metadata.copyright.lower()):
        font.font_metadata.copyright = expected_copyright
        messages.append("Metadata copyright updated")
        WriteMetadata(font.family_metadata, font.metadata_file)
    copyright_string = font.ttFont["name"].getName(NameID.COPYRIGHT_NOTICE, 3, 1)
    if not re.match(EXPECTED_COPYRIGHT_PATTERN, copyright_string.toUnicode().lower()):
        font.ttFont["name"].setName(
            expected_copyright, NameID.COPYRIGHT_NOTICE, 3, 1, 0x409
        )
        messages.append("Font copyright updated")
        font_changed = True
    if font.license_contents and not re.match(
        EXPECTED_COPYRIGHT_PATTERN, font.license_contents.lower()
    ):
        with open(font.license_path, "w", encoding="utf-8") as fp:
            fp.write(fix_ofl_license(font.ttFont) + "\n")
        messages.append("OFL rewritten")

    return font_changed, messages
