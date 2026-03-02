# Repository Guidelines

## Project Structure & Module Organization
- Root docs: `Readme.md`, `LICENSE`.
- Python automation: `Selenium/sel.py` with configs in `Selenium/config.json` and `Selenium/captcha_points.json`.
- Browser scripts: `js/*.js` (run in DevTools on the course site). Each file targets a specific selection strategy.
- Teaching notes: `Teach_Fishing/Readme.md`.

## Build, Test, and Development Commands
- Run Python script: `python3 Selenium/sel.py`
  - Configure first in `Selenium/config.json`; adjust captcha points in `Selenium/captcha_points.json`.
- Use a virtual env (recommended): `python3 -m venv .venv && source .venv/bin/activate && pip install selenium`
- Use JS scripts: open the course selection page, then paste a file such as `js/select_specfic_course.js` into the browser DevTools Console and press Enter.

## Coding Style & Naming Conventions
- Python: PEP 8, 4‑space indents, `snake_case` for functions/variables, `CapWords` for classes, constants in `ALL_CAPS`. File names like `lower_case_with_underscores.py`.
- JavaScript: 2‑space indents, `camelCase` for functions/variables, `PascalCase` for classes.
- Formatting (suggested): Python with `black` and `isort`; JS with `prettier`. Keep functions small and side‑effect aware.

## Testing Guidelines
- No formal suite exists. If adding logic, include minimal tests:
  - Python: create `tests/` with `test_*.py` and run `pytest -q`.
  - JS: factor logic into pure functions where possible and add quick checks (e.g., run in Console with sample inputs).
- Provide clear manual verification steps in PRs when automated tests aren’t feasible.

## Commit & Pull Request Guidelines
- Use Conventional Commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`.
- Branch names: `feature/<short-desc>` or `fix/<short-desc>`.
- PRs must include: concise description, context/linked issue, run steps, and before/after evidence (logs, screenshots, or Console output). Update docs if behavior changes.

## Security & Configuration Tips
- Do not commit credentials, cookies, or personal data. Keep local changes in untracked files or environment variables.
- Redact sensitive fields in `Selenium/config.json` before sharing. Avoid hard‑coding campus/course IDs in Python; prefer config or parameters.
