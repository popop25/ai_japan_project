from __future__ import annotations

from pathlib import Path

from ai_japan_project.storage import split_frontmatter


def parse_multiline(value: str) -> list[str]:
    return [line.strip() for line in value.splitlines() if line.strip()]


def get_latest_artifact(detail, kind: str):
    for artifact in detail.artifacts:
        if artifact.kind == kind:
            return artifact
    return None


def get_artifact_source(artifact) -> str:
    path = Path(str(artifact.path))
    if artifact.path and path.exists():
        return path.read_text(encoding="utf-8")
    return artifact.content


def summarize_text(value: str, limit: int = 140) -> str:
    compact = " ".join(line.strip() for line in value.splitlines() if line.strip())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 3].rstrip() + "..."


def first_markdown_paragraph(markdown: str) -> str:
    paragraph: list[str] = []
    for raw_line in markdown.splitlines():
        line = raw_line.strip()
        if not line:
            if paragraph:
                break
            continue
        if line.startswith("#"):
            if paragraph:
                break
            continue
        paragraph.append(line)
    return summarize_text(" ".join(paragraph))


def extract_markdown_outline(markdown: str, max_sections: int | None = None) -> list[dict[str, int | str]]:
    sections: list[dict[str, int | str]] = []
    current: dict[str, int | str] | None = None
    body_lines: list[str] = []

    for raw_line in markdown.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("#"):
            level = len(line) - len(line.lstrip("#"))
            title = line[level:].strip()
            if not title:
                continue
            if current is not None:
                current["summary"] = summarize_text(" ".join(body_lines)) or "세부 내용은 원문에서 확인하세요."
                sections.append(current)
                if max_sections is not None and len(sections) >= max_sections:
                    return sections
            current = {"level": level, "title": title, "summary": ""}
            body_lines = []
            continue
        body_lines.append(line)

    if current is not None:
        current["summary"] = summarize_text(" ".join(body_lines)) or "세부 내용은 원문에서 확인하세요."
        sections.append(current)

    if max_sections is None:
        return sections
    return sections[:max_sections]


def summarize_markdown_document(markdown: str, max_sections: int = 5) -> dict[str, str | int | list[dict[str, int | str]]]:
    outline = extract_markdown_outline(markdown)
    first_heading = next((section for section in outline if section["level"] == 1), None)
    title = str(first_heading["title"]) if first_heading else "문서 요약"
    summary = first_markdown_paragraph(markdown)
    if not summary and outline:
        summary = str(outline[0]["summary"])
    if not summary:
        summary = summarize_text(markdown) or "아직 요약을 만들 수 있는 본문이 없습니다."
    visible_sections = [section for section in outline if int(section["level"]) >= 2][:max_sections]
    if not visible_sections:
        visible_sections = outline[:max_sections]
    return {
        "title": title,
        "summary": summary,
        "sections": visible_sections,
        "section_count": len(outline),
    }


def inspect_pm_submission(markdown: str) -> dict[str, str | int]:
    stripped = markdown.strip()
    if not stripped:
        return {
            "state": "empty",
            "message": "제목 줄부터 문서 끝까지 한 번에 붙여넣으면 됩니다.",
            "section_count": 0,
        }

    outline = extract_markdown_outline(stripped)
    issues: list[str] = []
    first_line = stripped.splitlines()[0].strip()
    if not first_line.startswith("#"):
        issues.append("첫 줄이 Markdown 제목처럼 보이지 않습니다.")
    if len(stripped) < 120:
        issues.append("문서 길이가 너무 짧아 보입니다.")
    if len(outline) < 2:
        issues.append("주요 섹션이 거의 보이지 않습니다.")

    if issues:
        return {
            "state": "warning",
            "message": " ".join(issues),
            "section_count": len(outline),
        }
    return {
        "state": "ready",
        "message": f"{len(outline)}개 섹션이 감지되었습니다. 요구사항 초안 형태로 보입니다.",
        "section_count": len(outline),
    }


def inspect_critic_submission(markdown: str) -> dict[str, str | int]:
    stripped = markdown.strip()
    if not stripped:
        return {
            "state": "empty",
            "message": "Critic 답변 전체를 그대로 붙여넣어 주세요.",
            "missing_count": 0,
            "change_count": 0,
        }

    frontmatter, _ = split_frontmatter(markdown)
    if not frontmatter:
        return {
            "state": "warning",
            "message": "맨 위 YAML 블록(`---`)이 빠져 있습니다.",
            "missing_count": 0,
            "change_count": 0,
        }

    verdict = str(frontmatter.get("verdict", "")).strip()
    if verdict not in {"approve", "revise"}:
        return {
            "state": "warning",
            "message": "`verdict`는 `approve` 또는 `revise` 여야 합니다.",
            "missing_count": len(frontmatter.get("missing_items") or []),
            "change_count": len(frontmatter.get("recommended_changes") or []),
        }

    missing_count = len(frontmatter.get("missing_items") or [])
    change_count = len(frontmatter.get("recommended_changes") or [])
    verdict_label = "승인" if verdict == "approve" else "수정 필요"
    return {
        "state": "ready",
        "message": f"{verdict_label} 판단이 감지되었습니다. 누락 {missing_count}건, 수정 권고 {change_count}건.",
        "verdict": verdict,
        "summary": str(frontmatter.get("summary") or "").strip() or "요약이 비어 있습니다.",
        "missing_count": missing_count,
        "change_count": change_count,
    }


def get_workflow_stage(detail) -> str:
    if detail is None:
        return "create_task"
    if not detail.runs:
        return "create_pm_prompt"
    latest_run = detail.runs[0]
    if latest_run.stage == "pm" and latest_run.status == "packet_generated":
        return "ingest_pm_result"
    if latest_run.stage == "pm":
        return "create_critic_prompt"
    if latest_run.stage == "critic" and latest_run.status == "packet_generated":
        return "ingest_critic_review"
    return "review_outcome"


def workflow_steps(detail) -> list[dict[str, str]]:
    stage = get_workflow_stage(detail)
    order = {
        "create_task": 0,
        "create_pm_prompt": 1,
        "ingest_pm_result": 1,
        "create_critic_prompt": 2,
        "ingest_critic_review": 2,
        "review_outcome": 3,
    }[stage]
    return [
        {"index": "1", "title": "Context 확인", "description": "프로젝트 목적과 제약을 먼저 맞춥니다.", "state": "done"},
        {"index": "2", "title": "PM 초안 받기", "description": "PM 요청문을 만들고 초안을 반영합니다.", "state": "done" if order > 1 else "current" if order == 1 else "todo"},
        {"index": "3", "title": "Critic 리뷰 받기", "description": "검토 요청문을 만들고 리뷰를 반영합니다.", "state": "done" if order > 2 else "current" if order == 2 else "todo"},
        {"index": "4", "title": "판단 확인", "description": "승인 여부와 다음 조치를 확인합니다.", "state": "done" if order > 3 else "current" if order == 3 else "todo"},
    ]
