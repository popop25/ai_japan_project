# AI_Japan_project Context Brief

## Project
- 이름: AI_Japan_project
- 목적: 일본 고객사를 대상으로 AI 에이전트 업무 플랫폼의 실무 적용 가능성을 검증한다.
- 고객/대상: 일본 리테일 기업(가상)

## Current Status
- 현재 단계: 킥오프 완료, 요구사항 정의 진행 중
- 진행 중인 작업: PM 에이전트가 요구사항 정의서 초안을 작성할 수 있도록 맥락과 업무 흐름을 정리하는 단계
- 마지막 업데이트: 2026-03-28

## Constraints
- 기술 제약: Claude Code와 Codex 같은 외부 에이전트 handoff 방식을 유지한다.
- 일정 제약: 4주 PoC 안에 시연 가능한 데모를 완성해야 한다.
- 기타: 일본어 지원이 필요하고, 비개발자도 브라우저에서 흐름을 이해할 수 있어야 한다.

## Next Actions
1. 요구사항 정의서 초안 작성
2. Critic 리뷰 반영 프로세스 검증
3. 비개발자 시연용 UI 정리

## Decisions Log
- [2026-03-28] PM 에이전트를 첫 역할로 선정 / 임원과 비개발자에게 가장 이해하기 쉬운 산출물이기 때문
- [2026-03-28] 로컬 파일 저장소를 v1 canonical source로 사용 / Atlassian 연동 이전에도 end-to-end 데모를 완성하기 위함

## References
- Jira: v2에서 Jira TaskStore로 교체 예정
- Skills: project/skills/pm.md
- Notes: project/03_context.md
