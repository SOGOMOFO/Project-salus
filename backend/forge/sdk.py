import argparse
import sys
from pathlib import Path
from typing import Optional, Sequence

from backend.forge.generator import create_directorate


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python3 -m backend.forge.sdk")
    subparsers = parser.add_subparsers(dest="command")

    create_parser = subparsers.add_parser("create-directorate", help="Create a Salus directorate scaffold")
    create_parser.add_argument("name", help="Display name for the directorate")
    create_parser.add_argument(
        "--project-root",
        default=None,
        help="Path to the project root where files should be generated",
    )
    create_parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing generated files",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else sys.argv[1:])

    if not args.command:
        parser.print_help()
        return 1

    if args.command == "create-directorate":
        try:
            result = create_directorate(
                name=args.name,
                project_root=Path(args.project_root).resolve() if args.project_root else None,
                overwrite=args.overwrite,
            )
        except ValueError as exc:
            print(str(exc))
            return 1

        print(f"Created directorate '{result['directorate']}' ({result['slug']})")
        if result["created"]:
            print("Created files:")
            for item in result["created"]:
                print(f" - {item}")
        if result["skipped_existing"]:
            print("Skipped existing files:")
            for item in result["skipped_existing"]:
                print(f" - {item}")
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
