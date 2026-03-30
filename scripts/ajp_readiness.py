from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from ai_japan_project.operations import build_readiness_report, load_app_settings, render_readiness_report
from ai_japan_project.settings import AppMode


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run AI Japan Project readiness checks.")
    parser.add_argument("--mode", choices=[mode.value for mode in AppMode], help="Override runtime mode.")
    parser.add_argument("--dotenv", help="Optional path to a .env file.")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of a text summary.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    dotenv_path = Path(args.dotenv).resolve() if args.dotenv else None
    mode = AppMode(args.mode) if args.mode else None
    settings = load_app_settings(mode=mode, dotenv_path=dotenv_path)
    report = build_readiness_report(settings)
    if args.json:
        print(json.dumps(report.model_dump(mode="json"), ensure_ascii=False, indent=2))
    else:
        print(render_readiness_report(report), end="")
    return 0 if report.overall_status != "fail" else 1


if __name__ == "__main__":
    raise SystemExit(main())
