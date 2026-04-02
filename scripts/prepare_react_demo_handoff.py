from __future__ import annotations

from pathlib import Path
import textwrap


REPO_ROOT = Path(__file__).resolve().parents[1]
RUNS_DIR = REPO_ROOT / "project" / "runs"
ARTIFACTS_DIR = REPO_ROOT / "project" / "artifacts"

DRAFT_REQUEST_PATH = RUNS_DIR / "demo_requirements_draft_request.md"
REVIEW_REQUEST_PATH = RUNS_DIR / "demo_requirements_review_request.md"
DRAFT_OUTPUT_PATH = ARTIFACTS_DIR / "demo_requirements_draft.md"
REVIEW_OUTPUT_PATH = ARTIFACTS_DIR / "demo_requirements_review.md"


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).strip() + "\n", encoding="utf-8")


def draft_request() -> str:
    return f"""
    # Demo Request | 요구사항 정의서 초안 준비

    작업
    - 점포 운영 AI 적용 범위 정리

    역할
    - PM Agent

    목적
    - 점포 운영 문의 대응 업무를 기준으로 첫 적용 범위와 운영 원칙을 정리합니다.
    - 비개발자 팀도 바로 읽고 사용할 수 있는 요구사항 정의서 초안을 작성합니다.
    - 팀 공유 전에 남은 결정 사항과 빠진 담당자를 끝에 정리합니다.

    반드시 읽을 파일
    - project/03_context.md
    - project/skills/pm.md

    결과를 남길 파일
    - project/artifacts/demo_requirements_draft.md

    산출물
    - 요구사항 정의서 초안 1개
    - 열린 질문 목록 1개

    작업 지침
    1. 점포 운영 문의 대응 흐름에서 AI가 먼저 맡아야 할 범위를 분명하게 적습니다.
    2. 비개발자 운영 환경을 전제로 문서를 짧고 명확하게 작성합니다.
    3. 팀 공유 전에 확인할 담당자, 의존성, 마지막 판단 포인트를 명시합니다.
    4. 결과는 Markdown만 작성하고, 최종 파일은 지정된 결과 경로에 저장합니다.
    """


def review_request() -> str:
    return f"""
    # Demo Request | 요구사항 초안 검토 요청

    작업
    - 점포 운영 AI 적용 범위 정리

    역할
    - Critic Agent

    목적
    - 요구사항 정의서 초안이 팀 공유 가능한 수준인지 검토합니다.
    - 빠진 담당자, 미확정 결정, 운영 의존성을 짚어줍니다.
    - 운영자가 바로 최종 공유 판단을 할 수 있도록 verdict와 권장 수정 사항을 남깁니다.

    반드시 읽을 파일
    - project/03_context.md
    - project/skills/critic.md
    - project/artifacts/demo_requirements_draft.md

    결과를 남길 파일
    - project/artifacts/demo_requirements_review.md

    산출물
    - verdict: ready_for_decision 또는 revise
    - 요약
    - 권장 수정 사항

    작업 지침
    1. 공유 가능한 수준인지 먼저 판단합니다.
    2. 빠진 담당자와 운영 의존성을 짧고 명확하게 적습니다.
    3. 운영자가 다음으로 무엇을 해야 하는지 바로 이해할 수 있게 작성합니다.
    4. 결과는 Markdown만 작성하고, 최종 파일은 지정된 결과 경로에 저장합니다.
    """


def draft_output_placeholder() -> str:
    return """
    # 요구사항 정의서 초안

    이 파일은 personal agent가 작성합니다.
    """


def review_output_placeholder() -> str:
    return """
    ---
    verdict: ready_for_decision
    summary: ""
    recommended_changes: []
    ---

    이 파일은 personal agent가 작성합니다.
    """


def main() -> int:
    write_text(DRAFT_REQUEST_PATH, draft_request())
    write_text(REVIEW_REQUEST_PATH, review_request())
    write_text(DRAFT_OUTPUT_PATH, draft_output_placeholder())
    write_text(REVIEW_OUTPUT_PATH, review_output_placeholder())

    print("React demo handoff files prepared")
    print(f"- Draft request: {DRAFT_REQUEST_PATH.relative_to(REPO_ROOT)}")
    print(f"- Review request: {REVIEW_REQUEST_PATH.relative_to(REPO_ROOT)}")
    print(f"- Draft output: {DRAFT_OUTPUT_PATH.relative_to(REPO_ROOT)}")
    print(f"- Review output: {REVIEW_OUTPUT_PATH.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
