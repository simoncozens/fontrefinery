import argparse
import os
import sys
from pathlib import Path

from rich.table import Table
from rich import print

from fontrefinery.fixes import FixDirectory
from fontrefinery.testable import FixContext, Font


def main(args):
    parser = argparse.ArgumentParser(description="FontRefinery")
    gp = parser.add_mutually_exclusive_group()
    gp.add_argument("--fonts", nargs="+", help="Fonts to process", type=Font)
    gp.add_argument(
        "--directories", nargs="+", help="Directories to process", type=Path
    )

    parser.add_argument("--fix", nargs="+", help="Fixes to apply")
    args = parser.parse_args(args)
    if args.fonts:
        directories = [[args.fonts]]
    elif args.directories:
        directories = [
            [Font(str(file)) for file in directory.glob("*.?tf")]
            for directory in args.directories
        ]
    else:
        print("Must specify either --fonts or --directories")
        sys.exit(1)
    fixes = FixDirectory()
    wanted_fixes = [
        "com.google.fonts/check/family/win_ascent_and_descent",
        "com.google.fonts/check/font_copyright",
        "com.google.fonts/check/os2/use_typo_metrics",
        "com.google.fonts/check/fstype",
    ]
    for directory in directories:
        context = FixContext(directory)
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
