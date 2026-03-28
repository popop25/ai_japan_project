from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = REPO_ROOT / "project"
SKILLS_DIR = PROJECT_ROOT / "skills"
TASKS_DIR = PROJECT_ROOT / "tasks"
ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"
RUNS_DIR = PROJECT_ROOT / "runs"

CONTEXT_YAML_PATH = PROJECT_ROOT / "context.yaml"
CONTEXT_MARKDOWN_PATH = PROJECT_ROOT / "03_context.md"
PM_SKILL_PATH = SKILLS_DIR / "pm.md"
CRITIC_SKILL_PATH = SKILLS_DIR / "critic.md"