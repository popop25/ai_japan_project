# React Demo Shot List

## Goal

Show `AI_Japan_project` as a workspace that prepares the next handoff, lets the user work through their own agent, and finishes at a team-share destination preview.

The demo stays honest:

- React prepares the workflow
- the user's own agent does the work
- React confirms the next stage and the final share state

## Primary Scenario

- Task: `일본 런치 브리프`
- PM agent: `My Codex`
- Critic agent: `My Claude`
- Share outcome: `공유 상태 확인`

## Shot Sequence

1. `Task` 화면 진입
   - 보여줄 것: 현재 작업, 연결된 에이전트, 다음 행동
   - 멘트 요지: 프로젝트 맥락과 현재 작업이 이미 정리되어 있고, 지금 어떤 역할로 이어서 작업할지 보인다

2. `에이전트 전달` 화면 열기
   - 클릭: `전달 열기`
   - 보여줄 것: 브리프, 전달 방식, 현재 에이전트, 수동 handoff 안내
   - 멘트 요지: 이 앱이 직접 작업하지 않고, 내 에이전트로 넘길 브리프를 준비한다

3. `복사 후 붙여넣기` 유지 확인
   - 보여줄 것: `복사 후 붙여넣기` 선택 상태
   - 클릭: `에이전트에 보내기`
   - 멘트 요지: 브리프를 personal agent에 보낸다

4. 실제 personal agent 화면 1차
   - 짧게 보여줄 것: 브리프를 넣고 PM 작업을 이어가는 장면
   - 멘트 요지: 실제 작성 작업은 사용자의 에이전트에서 진행된다

5. React로 복귀
   - 클릭: `응답 준비됨 확인`
   - 이어서 클릭: `검토 요청`
   - 멘트 요지: 앱은 결과 자체를 소유하기보다, 다음 handoff 단계로 workflow를 이어준다

6. Critic handoff
   - 보여줄 것: Critic 브리프, 전달 대상이 `My Claude / Claude`로 바뀐 상태
   - 클릭: `에이전트에 보내기`
   - 멘트 요지: 같은 workspace 안에서 역할만 바꿔 다음 handoff를 준비한다

7. 실제 personal agent 화면 2차
   - 짧게 보여줄 것: Critic 역할로 검토하는 장면
   - 멘트 요지: Critic도 내장 시스템이 아니라 사용자의 에이전트 역할이다

8. React로 복귀
   - 클릭: `응답 준비됨 확인`
   - 화면: `검토 및 공유`
   - 멘트 요지: 이제 operator가 최종 팀 공유 상태를 확인한다

9. 팀 공유 준비
   - 클릭: `팀 공유 준비`
   - 이어서 클릭: `공유 상태 확인`
   - 보여줄 것: `팀 공유 상태`, `공유 대상`, `워크플로우 완료`
   - 멘트 요지: Jira와 Confluence는 기술 proof가 아니라 팀이 보게 될 공유 목적지다

## Timing Guide

- `Task`: 5~7초
- `Agent Handoff` PM: 8~10초
- personal agent PM: 5~7초
- Critic handoff + personal agent: 8~10초
- `Review & Share`: 8~10초

Total target: about 35~45 seconds before narration padding.

## Recording Notes

- Record at `1440px` width.
- Keep the browser zoom at the default level.
- Do not open actual Jira / Confluence pages in this cut.
- Keep `Task picker` and `Context` closed unless a later take needs them.
- Use the primary demo task only.
