import argparse
import os

from rich.table import Table
from rich import print

from fontrefinery.fixes import FixDirectory
from fontrefinery.testable import FixContext, Font


def main(args):
    parser = argparse.ArgumentParser(description="FontRefinery")
    parser.add_argument("fonts", nargs="+", help="Fonts to process", type=Font)
    parser.add_argument("--fix", nargs="+", help="Fixes to apply")
    args = parser.parse_args(args)
    context = FixContext(args.fonts)
    fixes = FixDirectory()
    wanted_fixes = [
        "com.google.fonts/check/family/win_ascent_and_descent",
        "com.google.fonts/check/font_copyright",
    ]
    for font in context.fonts:
        table = Table(title=os.path.basename(font.file))
        changed = False
        table.add_column("Fix")
        table.add_column("Messages")
        oldcolor = None
        for fix in wanted_fixes:
            fixname = fix.replace("com.google.fonts/check/", "")
            this_changed, this_messages = fixes[fix](font, context)
            color = "[yellow]" if this_changed else "[green]"
            for ix, message in enumerate(this_messages):
                if ix == 0 or color != oldcolor:
                    table.add_row(color + fixname, message)
                else:
                    table.add_row("", message)
                oldcolor = color
            changed |= this_changed
        if table.rows:
            print(table)
        if changed:
            font.ttFont.save(font.file)


if __name__ == "__main__":
    import sys

    main(sys.argv[1:])
