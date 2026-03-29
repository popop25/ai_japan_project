from __future__ import annotations

from pathlib import Path
from urllib.parse import parse_qs, urlparse
from uuid import uuid4

from ai_japan_project.atlassian import (
    AtlassianArtifactStore,
    AtlassianContextStore,
    build_page_body,
    page_url,
    parse_page_metadata,
)
from ai_japan_project.models import Artifact, Constraints, ProjectContext, References
from ai_japan_project.service import ProjectService
from ai_japan_project.storage import LocalContextStore, LocalRunStore, LocalTaskStore


TMP_ROOT = Path('.tmp_test_runs') / 'confluence_tests'


def make_test_root() -> Path:
    root = TMP_ROOT / uuid4().hex
    root.mkdir(parents=True, exist_ok=True)
    return root


class FakeConfluenceClient:
    def __init__(self, *, confluence_base_url: str = 'https://example.atlassian.net/wiki') -> None:
        self.confluence_base_url = confluence_base_url.rstrip('/')
        self.pages: dict[str, dict] = {}
        self._next_page_id = 1000

    def confluence_json(self, method: str, path: str, payload: dict | None = None) -> dict:
        parsed = urlparse(path)
        route = parsed.path
        query = parse_qs(parsed.query)

        if method == 'POST' and route == '/rest/api/content':
            page_id = str(self._next_page_id)
            self._next_page_id += 1
            page = {
                'id': page_id,
                'type': payload['type'],
                'title': payload['title'],
                'space': payload.get('space', {}),
                'ancestors': payload.get('ancestors', []),
                'body': {'storage': {'value': payload['body']['storage']['value']}},
                'version': {'number': 1},
            }
            self.pages[page_id] = page
            return self._page_response(page)

        if method == 'PUT' and route.startswith('/rest/api/content/'):
            page_id = route.split('/')[4]
            page = self.pages[page_id]
            page['title'] = payload['title']
            page['body'] = {'storage': {'value': payload['body']['storage']['value']}}
            page['version'] = {'number': payload['version']['number']}
            return self._page_response(page)

        if method == 'GET' and route.startswith('/rest/api/content/') and route.endswith('/child/page'):
            parent_page_id = route.split('/')[4]
            start = int(query.get('start', ['0'])[0])
            limit = int(query.get('limit', ['100'])[0])
            results = [
                self._page_response(page)
                for page in self.pages.values()
                if any(ancestor.get('id') == parent_page_id for ancestor in page.get('ancestors', []))
            ]
            return {'results': results[start : start + limit]}

        if method == 'GET' and route.startswith('/rest/api/content/'):
            page_id = route.split('/')[4]
            return self._page_response(self.pages[page_id])

        raise AssertionError(f'Unsupported fake Confluence call: {method} {path}')

    def _page_response(self, page: dict) -> dict:
        return {
            'id': page['id'],
            'type': page['type'],
            'title': page['title'],
            'space': dict(page.get('space', {})),
            'ancestors': [dict(item) for item in page.get('ancestors', [])],
            'body': {'storage': {'value': page['body']['storage']['value']}},
            'version': {'number': page['version']['number']},
        }


def test_parse_page_metadata_tolerates_prefix_offset_and_invalid_json() -> None:
    valid_body = '<p>prefix</p><!-- AJP_META:{&quot;artifact&quot;: {&quot;id&quot;: &quot;a1&quot;}}--><p>body</p>'
    invalid_body = '<!-- AJP_META:{not-json}--><p>body</p>'

    assert parse_page_metadata(valid_body) == {'artifact': {'id': 'a1'}}
    assert parse_page_metadata(invalid_body) == {}


def test_atlassian_context_store_bootstraps_and_preserves_markdown() -> None:
    project_dir = make_test_root() / 'project'
    project_dir.mkdir(parents=True, exist_ok=True)
    local_context = LocalContextStore(
        yaml_path=project_dir / 'context.yaml',
        markdown_path=project_dir / '03_context.md',
    )
    context = ProjectContext(
        name='Demo Project',
        purpose='Confluence context flow validation',
        customer='Test Customer',
        current_stage='context sync',
        active_work='03_Context canonical source sync',
        last_updated='2026-03-29',
        constraints=Constraints(
            technical='fake client only',
            schedule='this sprint',
            other='no live credentials',
        ),
        next_actions=['Align context metadata'],
        decisions=[],
        references=References(
            jira='KAN-1',
            skills='project/skills/pm.md',
            notes='project/03_context.md',
        ),
    )
    custom_markdown = '# Demo Context\n\n- custom markdown source\n'
    local_context.save(context, custom_markdown)
    client = FakeConfluenceClient()
    store = AtlassianContextStore(
        client,
        space_key='DEMO',
        parent_page_id='100',
        bootstrap_store=local_context,
    )

    loaded = store.load()
    loaded_markdown = store.load_markdown()

    assert loaded.name == 'Demo Project'
    assert loaded_markdown == custom_markdown
    created_page = next(iter(client.pages.values()))
    metadata = parse_page_metadata(created_page['body']['storage']['value'])
    assert metadata['context']['name'] == 'Demo Project'
    assert metadata['markdown'] == custom_markdown

    updated_context = loaded.model_copy(update={'active_work': 'updated remote canonical'})
    updated_markdown = '# Demo Context\n\n- updated remote canonical\n'
    store.save(updated_context, updated_markdown)

    saved_page = next(iter(client.pages.values()))
    saved_metadata = parse_page_metadata(saved_page['body']['storage']['value'])
    assert saved_page['version']['number'] == 2
    assert saved_metadata['context']['active_work'] == 'updated remote canonical'
    assert saved_metadata['markdown'] == updated_markdown


def test_atlassian_artifact_store_round_trips_page_url_and_metadata() -> None:
    client = FakeConfluenceClient()
    store = AtlassianArtifactStore(client, space_key='DEMO', parent_page_id='200')

    saved = store.save(
        Artifact(
            id='artifact_001',
            task_id='task_001',
            kind='pm_output',
            title='Requirements Draft',
            created_at='2026-03-29T00:00:00Z',
            path='',
            content='# Heading\n\n1. one\n2. two\n',
        )
    )

    page = next(iter(client.pages.values()))
    metadata = parse_page_metadata(page['body']['storage']['value'])
    assert saved.path == page_url(client.confluence_base_url, page['id'])
    assert metadata['artifact']['path'] == saved.path
    assert metadata['page']['url'] == saved.path
    assert '<ol>' in page['body']['storage']['value']

    updated = store.save(
        saved.model_copy(
            update={
                'title': 'Requirements Draft v2',
                'content': '# Updated Heading\n\n- stable page path\n',
            }
        )
    )

    updated_page = next(iter(client.pages.values()))
    updated_metadata = parse_page_metadata(updated_page['body']['storage']['value'])
    assert updated.path == saved.path
    assert updated_page['version']['number'] == 3
    assert updated_metadata['artifact']['title'] == 'Requirements Draft v2'
    assert updated_metadata['artifact']['path'] == saved.path


def test_project_service_keeps_remote_review_frontmatter_for_viewer() -> None:
    project_dir = make_test_root() / 'project'
    (project_dir / 'tasks').mkdir(parents=True, exist_ok=True)
    (project_dir / 'runs').mkdir(parents=True, exist_ok=True)
    context_store = LocalContextStore(
        yaml_path=project_dir / 'context.yaml',
        markdown_path=project_dir / '03_context.md',
    )
    context_store.save(
        ProjectContext(
            name='Demo Project',
            purpose='Remote artifact viewer validation',
            customer='Internal Team',
            current_stage='review',
            active_work='critic artifact display',
            last_updated='2026-03-29',
            constraints=Constraints(
                technical='remote artifact store',
                schedule='short validation',
                other='no live credentials',
            ),
            next_actions=[],
            decisions=[],
            references=References(
                jira='local',
                skills='project/skills/pm.md',
                notes='project/03_context.md',
            ),
        ),
        '# Context\n',
    )
    artifact_store = AtlassianArtifactStore(FakeConfluenceClient(), space_key='DEMO', parent_page_id='200')
    service = ProjectService(
        context_store=context_store,
        task_store=LocalTaskStore(project_dir / 'tasks'),
        artifact_store=artifact_store,
        run_store=LocalRunStore(project_dir / 'runs'),
    )
    detail = service.create_requirements_task('Remote review task')
    review_source = '''---
verdict: revise
summary: Needs stronger clarity.
missing_items:
  - success metrics
recommended_changes:
  - clarify scope
---
Please refine the acceptance criteria.
'''
    saved_review = artifact_store.save(
        Artifact(
            id='artifact_remote_review',
            task_id=detail.task.id,
            kind='critic_review',
            title='Critic Review',
            created_at='2026-03-29T10:00:00Z',
            path='',
            content=review_source,
        )
    )
    task = service.task_store.get(detail.task.id)
    assert task is not None
    service.task_store.save(task.model_copy(update={'artifact_ids': [saved_review.id]}))

    artifact = service.get_artifact(saved_review.id)
    detail = service.get_task_detail(detail.task.id)

    assert artifact is not None
    assert artifact.content.strip().startswith('---')
    assert 'Please refine the acceptance criteria.' in artifact.content
    assert detail.review is not None
    assert detail.review.verdict == 'revise'
    assert detail.artifacts[0].content == artifact.content



def test_atlassian_context_store_reuses_existing_plain_page_as_bootstrap_target() -> None:
    project_dir = make_test_root() / 'project'
    project_dir.mkdir(parents=True, exist_ok=True)
    local_context = LocalContextStore(
        yaml_path=project_dir / 'context.yaml',
        markdown_path=project_dir / '03_context.md',
    )
    context = ProjectContext(
        name='Bootstrap Project',
        purpose='Upgrade plain Confluence page into canonical context page',
        customer='Test Customer',
        current_stage='bootstrap',
        active_work='context migration',
        last_updated='2026-03-29',
        constraints=Constraints(
            technical='existing page without metadata',
            schedule='today',
            other='safe overwrite of canonical target',
        ),
        next_actions=['save canonical metadata'],
        decisions=[],
        references=References(
            jira='KAN-1',
            skills='project/skills/pm.md',
            notes='project/03_context.md',
        ),
    )
    local_context.save(context, '# Bootstrap Context\n\n- canonical markdown\n')
    client = FakeConfluenceClient()
    client.pages['98309'] = {
        'id': '98309',
        'type': 'page',
        'title': '03_Context',
        'space': {'key': 'DEMO'},
        'ancestors': [{'id': '100'}],
        'body': {'storage': {'value': '<h1>03_Context</h1><p>legacy plain page</p>'}},
        'version': {'number': 1},
    }
    store = AtlassianContextStore(
        client,
        space_key='DEMO',
        parent_page_id='100',
        bootstrap_store=local_context,
    )

    loaded = store.load()
    loaded_markdown = store.load_markdown()

    assert loaded.name == 'Bootstrap Project'
    assert loaded_markdown.startswith('# Bootstrap Context')
    upgraded_page = client.pages['98309']
    metadata = parse_page_metadata(upgraded_page['body']['storage']['value'])
    assert upgraded_page['version']['number'] == 2
    assert metadata['context']['name'] == 'Bootstrap Project'
    assert metadata['markdown'].startswith('# Bootstrap Context')


