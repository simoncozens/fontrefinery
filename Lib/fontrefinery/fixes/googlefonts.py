import re

from fontbakery.checks.googlefonts.conditions import family_metadata, font_metadata
from fontbakery.checks.googlefonts.constants import EXPECTED_COPYRIGHT_PATTERN
from fontbakery.checks.googlefonts.license import license_contents, license_path
from fontbakery.constants import NameID
from fontTools.misc.timeTools import timestampToString
from gftools.fix import fix_ofl_license
from gftools.util.google_fonts import WriteMetadata

from fontrefinery.fixes import FixResult, fix


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
