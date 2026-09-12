# Git Workflow for `frontend/adaptive`

The repository is a **monorepo**. The frontend application is located at:

```text
frontend/adaptive/
```

Follow these Git rules for all changes made to this project.

## 1. Commit Message Format

Every commit related to `frontend/adaptive` **must** use one of these Conventional Commit scopes:

```text
feat(frontend/adaptive): <description>
fix(frontend/adaptive): <description>
refactor(frontend/adaptive): <description>
docs(frontend/adaptive): <description>
style(frontend/adaptive): <description>
```

Choose the type based on the nature of the change:

- `feat` — new functionality
- `fix` — bug fix
- `refactor` — code restructuring without behavior changes
- `docs` — documentation-only changes
- `style` — formatting/UI styling changes

Do not use an unrelated scope such as `feat(frontend)` or `feat(adaptive)`.

## 2. Before Committing

Before creating a commit:

1. Make the required changes.
2. Run:

```bash
npm run check
```

3. Verify that the command reports:
   - **0 errors**
   - **0 warnings**

Do **not** commit if the check fails or reports warnings.

## 3. Creating the Commit

After validation succeeds:

```bash
git add <relevant-files>
git commit -m "<conventional commit message>"
```

Only include files relevant to the current change. Avoid committing unrelated modifications.

## 4. Pushing Changes

The working branch is:

```text
feat/exploratory-search-ui
```

Push it with:

```bash
git push origin feat/exploratory-search-ui
```

Do not push directly to `main` unless explicitly instructed.

## 5. Traceability

Because this is a monorepo, Git history must make it immediately clear that a commit belongs to `frontend/adaptive`.

Good:

```text
feat(frontend/adaptive): add result table
fix(frontend/adaptive): preserve results across turns
refactor(frontend/adaptive): simplify result rendering
docs(frontend/adaptive): update API guide
style(frontend/adaptive): improve conversation spacing
```

Bad:

```text
feat: add result table
feat(frontend): add result table
update frontend
fix stuff
changes
```

## 6. Agent Rule

For every completed development task:

```text
Make changes
    ↓
Run npm run check
    ↓
0 errors + 0 warnings?
    ├── No → Fix issues and run again
    └── Yes
          ↓
Create traceable commit
          ↓
Push to feat/exploratory-search-ui
```

The agent should **never skip validation**, create ambiguous commit messages, or mix unrelated changes into the same commit.
