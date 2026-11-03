# STATUS

Tracking list of everything that must be fixed in this repository. Update the
**Status** column as items land; keep one line per item in the summary table and
the details below it.

Last reviewed: 2026-11-03 (content update per `UPDATES-2026-11.md` applied the same day, brand restyle §9 deferred by decision)

## Summary

| # | Item | Priority | Status |
|---|------|----------|--------|
| 1 | Migrate off Heroku-22 (EOL 2027-04-30, builds disabled 2027-05-01) | **Critical** | Nearly done — `stack:set heroku-26` run 2026-11-03 (build stack = heroku-26); takes effect on the next deploy, i.e. merging the PR. Smoke-test after deploy (step 6 below) |
| 2 | `STATICFILES_STORAGE` / `DEFAULT_FILE_STORAGE` are ignored on Django 5.2 — manifest static storage is not active (S3 part is moot: no AWS vars exist on the app) | Medium | Done on branch (`STORAGES` dict; `collectstatic` verified locally, 215 files) |
| 3 | Pin the stack in `app.json` so Review Apps / fresh deploys use the new stack | Medium | Done (`"stack": "heroku-26"`, on branch `feature/site-updates-2026-11`) |
| 4 | Add a lint/format tool (`ruff`) and a minimal CI workflow | Medium | Open |
| 5 | Test files are empty stubs — `manage.py test` is not a real gate | Medium | Open |
| 6 | `core/settings.py` header still references Django 2.0 docs | Low | Open |
| 7 | README project structure lists a top-level `static/` that does not exist | Low | Open |
| 8 | Content: PPGMIT master's entry says "in selection" — update with the result after 2026-12-16 (home.html Education + Research sections) | Low | Scheduled |
| 9 | `pyproject.toml` and `app.json` `description` still read "Engineering Leader & Cybersecurity Expert" | Low | Open |
| 10 | `/research`: swap the MEISTUDIES extended summary for the full English text + DOI once the congress routes the paper (ebook or journal) | Medium | Waiting on venue |
| 14 | `/research`: link the SIMPEP proceedings entry (ISBN, pages) under `#simpep-2026` once the anais are published; check whether the anais byline carries "Filho" | Low | Waiting on anais |
| 11 | `/workshops/<pk>` raises `AttributeError` when the `Workshop` table is empty (`workshops/views.py:15`, `.first()` unguarded) and ignores `pk` | Low | Open |
| 12 | Production ran on the hard-coded fallback `SECRET_KEY` (`core/settings.py:24`); the app had no config vars | **High** | Done — `SECRET_KEY` config var set 2026-11-03 (release v27) |
| 13 | `python-journey` (another app on this account) is also on heroku-22, last deployed 2022 — same EOL deadlines | Low | Open |

## Details

### 1. Migrate off Heroku-22

Source: https://help.heroku.com/NQNCQTEJ/heroku-22-end-of-life-faq

Timeline that affects this app:

| Date | Effect |
|------|--------|
| 2026-05-20 | Heroku-22 deprecated |
| **2026-11-01** | First build in every 30-day window fails with a deprecation error (retrigger deploys normally) — **already in effect** |
| 2027-02-01 | Error on first build in every 7-day window |
| 2027-04-01 | Error on first build in every 24-hour window |
| 2027-04-30 | Heroku-22 end-of-life: app keeps running, no more security updates |
| 2027-05-01 | Builds disabled for all Heroku-22 apps (incl. Review Apps, CI). No extensions. |

Current state (checked 2026-11-03 with the Heroku CLI):

- App `ariedi` is on **heroku-22** (confirmed), buildpack `heroku/python`, one web dyno, region us,
  current release v26 = commit `5f6e0f2` (deployed 2026-04-11). heroku-24 and heroku-26 are offered.
- No config vars, no add-ons (see item 12).
- `app.json` declares no `stack`, so new Review Apps / `heroku create` default to whatever Heroku
  currently defaults to — pinning it removes the ambiguity (see item 3).
- Runtime: Python 3.12 via `.python-version`. The Heroku Python buildpack supports 3.12 on both
  Heroku-24 and Heroku-26, so no Python version change is required for the stack move.
- Native deps that get rebuilt against the new base image: `psycopg2-binary` and `pillow`
  (both ship wheels; low risk).

Fix:

1. ~~Confirm the stack~~ done: heroku-22.
2. Pick the target stack. Prefer **heroku-26** (released 2026-05, longest runway); fall back to
   **heroku-24** if the buildpack or any dependency misbehaves on 26.
3. Test first on a Review App / staging app with the new stack set.
4. ~~Set it on production~~ done 2026-11-03: `heroku stack:set heroku-26 -a ariedi`.
5. Trigger a deploy (an empty commit is enough: `git commit --allow-empty -m "chore: rebuild on heroku-26"`
   then push). The stack change only takes effect on the next build.
6. Smoke-test: home page, presentations page (PDF embed), admin login, `collectstatic` output,
   media upload (after item 2 is fixed), contact form email.
7. Rollback plan: `heroku rollback` to the previous release (do **not** use `stack:set heroku-22`).

### 2. Storage settings silently ignored on Django 5.2

`core/settings.py:128` sets `STATICFILES_STORAGE` and `core/settings.py:148` sets
`DEFAULT_FILE_STORAGE`. Both were deprecated in Django 4.2 and **removed in Django 5.1**; the project
is on 5.2.8, so Django ignores them and falls back to defaults.

Checked on 2026-11-03 with the Heroku CLI: the `ariedi` app has **no config vars and no add-ons**, so
there is no S3 bucket, no Postgres and no SMTP in production. Consequences, re-assessed:

- Media: already on `FileSystemStorage` and nothing uploads media (Projects/Workshops are not live), so
  the S3 half of this item is moot. Do **not** switch `default` to S3 — it would raise on first use.
- Static: served by WhiteNoise middleware but as plain `StaticFilesStorage` — no hashed filenames,
  no far-future caching, no pre-compression. This is the half worth fixing.

Revised fix — replace both old settings with:

```python
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}
```

Keep the `AWS_*` lines only if S3 is coming back; otherwise delete them and the `storages` app.
Manifest storage makes `collectstatic` **fail the Heroku build** if any template or CSS references a
missing static file, so run `python manage.py collectstatic --noinput` locally before pushing.

### 3. Pin the stack in `app.json`

Add `"stack": "heroku-26"` (or `heroku-24`, matching item 1) to `app.json` so Review Apps and
button deploys never land on a deprecated stack again.

### 4. Lint/format + CI

No linter, formatter, or GitHub Actions workflow exists (`.github/` only holds a PR template).
Add `ruff` to the dev dependencies with `ruff check` + `ruff format --check`, and a workflow that
runs them plus `python manage.py test` on pull requests.

### 5. Empty test stubs

All four `tests.py` files contain only the default `TestCase` import. `app.json` runs
`python manage.py test` in the Heroku CI test environment, so it always passes trivially. At
minimum add smoke tests for each URL in `core/urls.py`, `pages/urls.py`, `workshops/urls.py`
(status 200) and one for the contact form POST path (`pages/views.py`).

### 6. Stale settings header

`core/settings.py:1-11` says the file was generated by Django 2.0 and links to 2.0 docs. Update
the links to the 5.2 docs when touching the file for item 2.

### 7. README structure drift

`README.md` lists `static/` at the repo root; static assets actually live in `pages/static/`.
Fix the tree in the README.
