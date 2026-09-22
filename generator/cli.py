"""Generate the polar-effect SDK from Polar's OpenAPI specs."""

import argparse
import json
import os
import pathlib
import shutil
import sys

# Upstream's IR builder iterates sets in places, so output depends on hash randomization.
if os.environ.get("PYTHONHASHSEED") != "0":
    os.execve(
        sys.executable,
        [sys.executable, *sys.argv],
        {**os.environ, "PYTHONHASHSEED": "0"},
    )

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(1, str(ROOT / "upstream" / "sdk" / "generator"))

import openapi_pydantic as op

from effect.emitter import EffectEmitter
from generator.ir import generate_ir

DEFAULT_SPECS = [ROOT / "upstream" / "docs" / "openapi" / "2026-10.openapi.json"]
DEFAULT_OUTPUT = ROOT / "sdk"


def current_version(output: pathlib.Path) -> str:
    package_json = output / "package.json"
    if package_json.exists():
        return json.loads(package_json.read_text(encoding="utf-8"))["version"]
    return "0.0.0"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "specs",
        nargs="*",
        type=pathlib.Path,
        default=DEFAULT_SPECS,
        help="OpenAPI spec files, one per API version (default: 2026-10).",
    )
    parser.add_argument("--output", type=pathlib.Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--version",
        help="Package version (default: the version currently in sdk/package.json).",
    )
    parser.add_argument(
        "--skip-checks",
        action="store_true",
        help="Skip install, format, lint, typecheck, build and test after emitting.",
    )
    args = parser.parse_args()

    version = args.version or current_version(args.output)
    specs = [
        op.OpenAPI.model_validate_json(path.read_text(encoding="utf-8"))
        for path in args.specs
    ]
    ir = generate_ir(*specs)

    if args.output.exists():
        for child in args.output.iterdir():
            if child.name == "node_modules":
                continue
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink()

    emitter = EffectEmitter(ir, version)
    emitter.emit(args.output)
    if not args.skip_checks:
        emitter.run_post_actions(args.output)


if __name__ == "__main__":
    main()
