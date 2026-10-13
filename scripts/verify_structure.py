"""Check the scaffold layout only; this does not validate application behavior."""
import json
import sys
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[1]
    try:
        manifest = json.loads((root / "scaffold-manifest.json").read_text(encoding="utf-8"))
        required = manifest["required_files"]
    except (OSError, ValueError, KeyError) as exc:
        print(f"FAIL: cannot read scaffold manifest: {exc}")
        return 1
    missing = [name for name in required if not (root / name).is_file()]
    if missing:
        print("FAIL: missing scaffold files:")
        for name in missing:
            print(f"  {name}")
        return 1
    print("PASS: all scaffold files exist. Application functionality is not tested.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
