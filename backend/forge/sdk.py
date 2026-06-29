import argparse
import sys
from pathlib import Path
from typing import Optional, Sequence

from backend.forge.generator import create_directorate, discover_plugins, disable_plugin, enable_plugin, rollback_directorate
from backend.forge.validator import validate_directorate_structure


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python3 -m backend.forge")
    subparsers = parser.add_subparsers(dest="command")

    create_parser = subparsers.add_parser("create-directorate", help="Create a Salus directorate scaffold")
    create_parser.add_argument("name", help="Display name for the directorate")
    create_parser.add_argument("--project-root", default=None, help="Path to the project root where files should be generated")
    create_parser.add_argument("--overwrite", action="store_true", help="Overwrite existing generated files")

    list_parser = subparsers.add_parser("list", help="List generated directorates")
    list_parser.add_argument("--project-root", default=None, help="Path to the project root")

    validate_parser = subparsers.add_parser("validate", help="Validate generated directorates")
    validate_parser.add_argument("--project-root", default=None, help="Path to the project root")

    rollback_parser = subparsers.add_parser("rollback", help="Rollback a generated directorate")
    rollback_parser.add_argument("name", nargs="?", default=None, help="Display name for the directorate")
    rollback_parser.add_argument("--project-root", default=None, help="Path to the project root")

    plugins_parser = subparsers.add_parser("plugins", help="List discovered directorate plugins")
    plugins_parser.add_argument("--project-root", default=None, help="Path to the project root")

    enable_parser = subparsers.add_parser("enable", help="Enable a directorate plugin")
    enable_parser.add_argument("plugin", help="Plugin slug")
    enable_parser.add_argument("--project-root", default=None, help="Path to the project root")

    disable_parser = subparsers.add_parser("disable", help="Disable a directorate plugin")
    disable_parser.add_argument("plugin", help="Plugin slug")
    disable_parser.add_argument("--project-root", default=None, help="Path to the project root")
    return parser


def _list_directorates(project_root: Path) -> list[str]:
    directorates_dir = project_root / "backend" / "directorates"
    if not directorates_dir.exists():
        return []
    return sorted([path.name for path in directorates_dir.iterdir() if path.is_dir() and (path / "__init__.py").exists()])


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else sys.argv[1:])

    if not args.command:
        parser.print_help()
        return 1

    project_root = Path(args.project_root).resolve() if getattr(args, "project_root", None) else None

    if args.command == "create-directorate":
        try:
            result = create_directorate(name=args.name, project_root=project_root, overwrite=args.overwrite)
        except (ValueError, RuntimeError) as exc:
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

    if args.command == "list":
        for directorate in _list_directorates(project_root or Path.cwd()):
            print(directorate)
        return 0

    if args.command == "validate":
        root = project_root or Path.cwd()
        try:
            for slug in _list_directorates(root):
                validate_directorate_structure(root, slug, slug.replace("_", " ").title())
            print("Validation succeeded")
            return 0
        except ValueError as exc:
            print(str(exc))
            return 1

    if args.command == "rollback":
        if not args.name:
            print("Rollback requires a directorate name")
            return 1
        try:
            rollback_directorate(args.name, project_root=project_root)
        except (ValueError, RuntimeError) as exc:
            print(str(exc))
            return 1
        print(f"Rolled back '{args.name}'")
        return 0

    if args.command == "plugins":
        for plugin in discover_plugins(project_root or Path.cwd()):
            enabled = "enabled" if plugin["enabled"] else "disabled"
            print(f"{plugin['slug']} ({plugin['version']}) [{enabled}]")
        return 0

    if args.command == "enable":
        try:
            result = enable_plugin(args.plugin, project_root=project_root)
        except (ValueError, RuntimeError) as exc:
            print(str(exc))
            return 1
        print(f"Enabled plugin '{result['slug']}'")
        return 0

    if args.command == "disable":
        try:
            result = disable_plugin(args.plugin, project_root=project_root)
        except (ValueError, RuntimeError) as exc:
            print(str(exc))
            return 1
        print(f"Disabled plugin '{result['slug']}'")
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
