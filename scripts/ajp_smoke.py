from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from ai_japan_project.operations import SMOKE_PREFIX, load_app_settings, run_atlassian_smoke
from ai_japan_project.settings import AppMode


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the AI Japan Project live Atlassian smoke flow.")
    parser.add_argument("--mode", choices=[mode.value for mode in AppMode], default=AppMode.ATLASSIAN.value, help="Runtime mode override. Defaults to atlassian.")
    parser.add_argument("--dotenv", help="Optional path to a .env file.")
    parser.add_argument("--prefix", default=SMOKE_PREFIX, help="Prefix used for generated smoke resources.")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of a text summary.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    dotenv_path = Path(args.dotenv).resolve() if args.dotenv else None
    settings = load_app_settings(mode=AppMode(args.mode), dotenv_path=dotenv_path)
    receipt = run_atlassian_smoke(settings, prefix=args.prefix)
    if args.json:
        print(json.dumps(receipt.model_dump(mode="json"), ensure_ascii=False, indent=2))
    else:
        print("AI Japan Project smoke run completed")
        print(f"- Jira issue: {receipt.jira_issue_key} ({receipt.jira_issue_url})")
        print(f"- PM artifact: {receipt.pm_artifact_url}")
        print(f"- Critic review: {receipt.critic_review_url}")
        print(f"- Final status: {receipt.final_status}")
        print(f"- Receipt: {receipt.receipt_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
