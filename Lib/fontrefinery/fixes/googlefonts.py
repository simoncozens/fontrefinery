import os
import re

# Conditions
import fontbakery.checks.googlefonts.conditions
import fontbakery.checks.googlefonts.description
import fontbakery.checks.googlefonts.license

from fontbakery.checks.googlefonts.constants import EXPECTED_COPYRIGHT_PATTERN
from fontbakery.constants import NameID
from fontTools.misc.timeTools import timestampToString
from gftools.fix import fix_ofl_license
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
    return False, ["Git URL added to DESCRIPTION"]
