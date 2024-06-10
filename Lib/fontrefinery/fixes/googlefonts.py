import os
import re

# Conditions
import fontbakery.checks.googlefonts.conditions
import fontbakery.checks.googlefonts.description
import fontbakery.checks.googlefonts.license

from fontbakery.checks.googlefonts.constants import EXPECTED_COPYRIGHT_PATTERN
from fontbakery.constants import NameID, PLACEHOLDER_LICENSING_TEXT
from fontTools.misc.timeTools import timestampToString
from gftools.fix import fix_ofl_license
from gftools.fix import remove_tables
from gftools.utils import font_stylename, remove_url_prefix
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
def fix_fs_selection(font: Font, _context) -> FixResult:
    """Fix the OS/2 table's fsSelection so it conforms to GF's supported
    styles table:
    https://github.com/googlefonts/gf-docs/tree/main/Spec#supported-styles
    """
    ttFont = font.ttFont
    stylename = font_stylename(ttFont)
    tokens = set(stylename.split())

    # This is different to gftools-fix, we explicitly set TYPO_METRICS bit
    if ttFont["OS/2"].version >= 4:
        fs_selection = 1 << 7
    else:
        fs_selection = 0

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
        "com.google.fonts/check/metadata/consistent_repo_urls",
    ]
)
def fix_font_copyright(font, _context) -> FixResult:
    if not font.family_metadata:
        return False, ["[bright_red]Metadata is missing[/bright_red]"]
    if not font.font_metadata:
        return False, [
            "[bright_red]Metadata present but font metadata missing[/bright_red]"
        ]
    if not font.family_metadata.source.repository_url:
        return False, ["[red]Repository URL is missing in METADATA.pb[/red]"]

    if "reserved font name" in font.font_metadata.copyright.lower():
        return False, ["[red]Reserved font name found in copyright[/red]"]

    font_year = timestampToString(font.ttFont["head"].created)[-4:]
    md_year = font.family_metadata.date_added[:4]
    if font_year > md_year:
        font_year = md_year
    expected_copyright = f"Copyright {font_year} The {font.family_metadata.name} Project Authors ({font.family_metadata.source.repository_url})"
    messages = []
    font_changed = False
    if not re.match(EXPECTED_COPYRIGHT_PATTERN, font.font_metadata.copyright.lower()):
        font.font_metadata.copyright = expected_copyright
        messages.append("Metadata copyright updated")
        WriteMetadata(font.family_metadata, font.metadata_file)

    # This doesn't yet handle Mac platform names...
    copyright_string = font.ttFont["name"].getName(NameID.COPYRIGHT_NOTICE, 3, 1)
    if not re.match(EXPECTED_COPYRIGHT_PATTERN, copyright_string.toUnicode().lower()):
        font.ttFont["name"].setName(
            expected_copyright, NameID.COPYRIGHT_NOTICE, 3, 1, 0x409
        )
        messages.append("Font copyright updated")
        font_changed = True
    # ...so let's remove them if there
    for nameRecord in font.ttFont["name"].names:
        if nameRecord.nameID == NameID.COPYRIGHT_NOTICE and nameRecord.platformID == 1:
            font.ttFont["name"].names.remove(nameRecord)
            font_changed = True
            messages.append("Removed Mac copyright")
    if font.license_contents and not re.match(
        EXPECTED_COPYRIGHT_PATTERN, font.license_contents.lower()
    ):
        with open(font.license_path, "w", encoding="utf-8") as fp:
            try:
                fp.write(fix_ofl_license(font.ttFont) + "\n")
                messages.append("OFL rewritten")
            except ValueError:
                messages.append("[red]OFL could not be rewritten (RFN?)[/red]")

    return font_changed, messages


@fix(
    id=[
        "com.google.fonts/check/description/git_url",
    ]
)
def fix_description_git_url(font, _context) -> FixResult:
    if not font.family_metadata or not font.family_metadata.source.repository_url:
        return False, []

    if not font.description or font.description_html is None:
        return False, ["[bright_red]Description is missing[/bright_red]"]

    git_urls = []
    for a_href in font.description_html.iterfind(".//a[@href]"):
        link = a_href.get("href")
        if "://git" in link:
            git_urls.append(link)

    if git_urls:
        return False, []
    github_url = font.family_metadata.source.repository_url
    description = font.description
    human_url = remove_url_prefix(github_url)
    description += (
        f'\n<p>To contribute, please see <a href="{github_url}">{human_url}</a>.</p>'
    )
    descfile = os.path.join(os.path.dirname(font.file), "DESCRIPTION.en_us.html")
    with open(descfile, "w", encoding="utf-8") as f:
        f.write(description)
    return False, ["'To contribute' URL added to DESCRIPTION"]


@fix(id="com.google.fonts/check/integer_ppem_if_hinted")
def fix_integer_ppem_if_hinted(font, _context) -> FixResult:
    """Hinted fonts must have head table flag bit 3 set"""
    if not font.is_hinted:
        return False, []
    if not font.ttFont["head"].flags & (1 << 3):
        font.ttFont["head"].flags |= 1 << 3
        return True, ["Set head table bit 3 (integer ppem)"]
    return False, []


@fix(id="com.google.fonts/check/name/license")
def fix_name_license(font, _context) -> FixResult:
    if not font.family_metadata:
        return False, []
    updated = False
    placeholder = PLACEHOLDER_LICENSING_TEXT[font.license_filename]
    for i, nameRecord in enumerate(font.ttFont["name"].names):
        if nameRecord.nameID == NameID.LICENSE_DESCRIPTION:
            value = nameRecord.toUnicode()
            if value != placeholder:
                nameRecord.string = placeholder.encode(nameRecord.getEncoding())
                updated = True
        if (
            nameRecord.nameID == NameID.LICENSE_INFO_URL
            and font.license_filename == "OFL.txt"
        ):
            value = nameRecord.toUnicode()
            if value != "https://openfontlicense.org":
                nameRecord.string = "https://openfontlicense.org".encode(
                    nameRecord.getEncoding()
                )
                updated = True
    if updated:
        return True, ["Updated name table license description"]
    return False, []


@fix(id="com.google.fonts/check/metadata/subsets_order")
def fix_subsets_order(font, _context) -> FixResult:
    if not font.family_metadata:
        return False, []
    sorted_subsets = sorted(font.family_metadata.subsets)
    if font.family_metadata.subsets != sorted_subsets:
        del font.family_metadata.subsets[:]
        font.family_metadata.subsets.extend(sorted_subsets)
        WriteMetadata(font.family_metadata, font.metadata_file)
        return True, ["Subsets reordered"]
    return False, []


@fix("com.google.fonts/check/unwanted_tables")
def fix_unwanted_tables(font: Font, _context) -> FixResult:
    return remove_tables(font.ttFont)
