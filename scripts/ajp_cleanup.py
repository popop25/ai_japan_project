from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from ai_japan_project.operations import SMOKE_PREFIX, cleanup_smoke_receipts, load_app_settings, render_cleanup_plan
from ai_japan_project.settings import AppMode


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Clean up AI Japan Project smoke resources.")
    parser.add_argument("--mode", choices=[mode.value for mode in AppMode], default=AppMode.ATLASSIAN.value, help="Runtime mode override. Defaults to atlassian.")
    parser.add_argument("--dotenv", help="Optional path to a .env file.")
    parser.add_argument("--prefix", default=SMOKE_PREFIX, help="Receipt prefix to clean up.")
    parser.add_argument("--apply", action="store_true", help="Actually delete Jira, Confluence, and local smoke resources.")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of a text summary.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    dotenv_path = Path(args.dotenv).resolve() if args.dotenv else None
    settings = load_app_settings(mode=AppMode(args.mode), dotenv_path=dotenv_path)
    plan = cleanup_smoke_receipts(settings, prefix=args.prefix, apply=args.apply)
    if args.json:
        print(json.dumps(plan.model_dump(mode="json"), ensure_ascii=False, indent=2))
    else:
        print(render_cleanup_plan(plan), end="")
    failed = any(target.status == "failed" for target in plan.targets)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
