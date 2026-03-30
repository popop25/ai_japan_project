# Operations

## Configuration Strategy

The app resolves settings in this order:

1. operating system environment variables
2. repository `.env`

This means you can keep a local `.env` for convenience while still overriding values in a one-off shell session.

## Runtime Commands

### Run the Streamlit app

```powershell
python -m streamlit run app_ui/streamlit_app.py
```

### Run readiness / preflight

```powershell
python scripts/ajp_readiness.py
python scripts/ajp_readiness.py --mode atlassian
python scripts/ajp_readiness.py --mode atlassian --json
```

### Run the live Atlassian smoke flow

```powershell
python scripts/ajp_smoke.py
python scripts/ajp_smoke.py --prefix "[AJP Smoke]"
python scripts/ajp_smoke.py --json
```

### Preview smoke cleanup

```powershell
python scripts/ajp_cleanup.py
python scripts/ajp_cleanup.py --json
```

### Apply smoke cleanup

```powershell
python scripts/ajp_cleanup.py --apply
```

### Run tests

```powershell
pytest tests -q --basetemp=.tmp_test_runs\pytest
```

## What Readiness Checks

In `local` mode readiness verifies:

- canonical context files exist
- skill files exist
- runtime directories are ready or creatable

In `atlassian` mode readiness verifies:

- Atlassian configuration is valid
- Jira identity is reachable
- the configured Jira project is reachable
- Jira exposes the `search/jql` endpoint used by the harness
- expected workflow aliases are available, including localized variants where needed
- Confluence context and artifact parent pages are reachable
- tenant-specific assumptions are surfaced explicitly

## What the Smoke Flow Does

The smoke flow performs a minimal end-to-end run against the configured Atlassian tenant:

1. upsert `03_Context`
2. create a Jira-backed requirements task
3. generate a PM packet locally
4. ingest a canned PM draft
5. generate a Critic packet locally
6. ingest a canned Critic review
7. persist a JSON receipt under `project/runs/smoke_receipts/`

Smoke resources use the `[AJP Smoke]` prefix so they can be found and cleaned safely.

## What Cleanup Does

Cleanup is receipt-driven.

A dry run collects the resources associated with saved smoke receipts:

- Jira issues
- Confluence PM artifact pages
- Confluence Critic review pages
- local packet files
- receipt files

`--apply` then attempts deletion while continuing past missing resources and recording failures.

## Tenant Notes Captured in Code

The current integration hardens for live behaviors that appeared in the connected Atlassian tenant:

- Jira search uses `POST /rest/api/3/search/jql`
- Jira workflow names may be localized, including Korean aliases such as `?? ? ?`, `?? ?`, and `??`
- Confluence metadata must survive storage-body normalization, so canonical metadata is also stored in a content property fallback

These are treated as operational assumptions, not one-off hacks.

## Recovery Guidance

### Readiness fails before smoke

Fix the failing check first. The smoke run is intentionally not the first diagnostic tool.

### Smoke creates resources but stops mid-run

Run cleanup in dry-run mode first, inspect the planned targets, then rerun with `--apply` if the resources are safe to remove.

### Jira status sync fails

Check the readiness report for workflow alias coverage and confirm the configured project exposes a `Task` issue type.

### Confluence pages appear without metadata

This tenant strips or normalizes some storage details. The harness uses content properties as the fallback canonical metadata source, so verify that page property writes still succeed.
