# Publish InferEdge Entrypoint

This repository is the public InferEdge ecosystem entrypoint. It already has a
real `main` history, so publishing work must preserve that history. Do not force
push over `main` to import another local repository.

## Pre-publish Checks

Run the focused local tests from the repository root:

```bash
python -m pytest -q
```

Run a whitespace and patch sanity check before staging or pushing:

```bash
git diff --check
```

After staging files, repeat the check against the staged patch before
committing:

```bash
git diff --cached --check
```

When the sibling repositories are available, run the cross-repo portfolio smoke:

```bash
bash scripts/smoke_all.sh
```

Before pushing, run the publish readiness check:

```bash
bash scripts/check_publish_ready.sh
```

The README reviewer verification helper runs the same local verification order
as a single entrypoint:

```bash
bash scripts/check_reviewer_verification_set.sh
```

Use `--dry-run` on that helper when you only need to confirm the command order.
Use `--log-dir /tmp/inferedge_reviewer_verification_logs` when full smoke output
is too long for the terminal but the per-step logs should be preserved.
It does not replace the staged `git diff --cached --check` before committing.

The readiness check verifies:

- current branch
- latest commit
- working tree cleanliness
- `origin` remote presence
- `origin` remote placeholder detection
- `origin` remote reachability
- `origin` branch fast-forward safety
- local `main` checkout safety
- suggested push command

Expected safe output on `main` includes
`Local main safety: upstream matches origin/main`,
`Origin branch state: publishable`, `Upstream: origin/main`, and
`Suggested publish command: git push`. Treat any
`Publish readiness: blocked` or `Publish readiness: failed` line as a stop
signal, not as a prompt to bypass the check.

## Safe Branch Publish

Start from the current remote `main` and publish a review branch:

```bash
git fetch origin main
git switch -c codex/<topic> origin/main
git diff --check
python -m pytest -q
bash scripts/check_publish_ready.sh
git push -u origin codex/<topic>
```

If the check reports `Upstream status: different branch`, use the suggested
`git push -u origin <current-branch>` command instead of plain `git push`.

If the check reports `Local main safety: review before publishing`, stop there.
Do not push local `main` directly; create a review branch from `origin/main`
and publish the branch instead.

## Bundled PR Merge Step

For small documentation, workflow, or marker-test changes, treat branch
publishing, PR creation, and PR merge as one execution step after local
validation passes. Do not commit, push, open a PR, or merge while any required
test or smoke check is failing.

Do not split the validated publish, PR creation, and merge handoff into
separate reviewer instructions unless a failed check or unresolved review
comment requires stopping.

Before merging, verify the changed file list is scoped to the intended task and
the pull request is mergeable. After merging, fetch `origin/main`, confirm the
new merge commit, and start the next task from `origin/main`.

Use this PR merge gate inside the bundled step:

1. Confirm the PR changed-file list matches the local diff scope.
2. Confirm the PR is not a draft and GitHub reports it as mergeable.
3. Confirm commit status checks have no failures. If the repository has no
   configured checks, record that no failing GitHub statuses were reported and
   rely on the local validation commands listed in the PR body.
4. Merge with the expected head SHA so a moved branch cannot be merged by
   accident.

The PR body should include a short `Summary` and `Tests` section. List the
exact validation commands that passed so reviewers can connect the merge to the
local checks.

## GitHub Auth Fallback

Use the GitHub connector/app for PR creation and merge when it is available.
The `gh` CLI is a fallback path, not a required source of validation evidence.

If `gh auth status` reports an invalid token, do not treat that as a failed
test or smoke result. Either re-authenticate before using the CLI fallback:

```bash
gh auth login -h github.com
```

or continue with the authenticated GitHub connector/app. When the connector is
used because the local `gh` token is invalid, note that in the PR body so the
publish path remains auditable.

## Final Status Check

Before considering the publish step complete, verify the local checkout has no
unexpected working-tree or staged changes:

```bash
git status --short --branch
git diff --stat
git diff --cached --stat
```

If any unexpected file appears, investigate it before starting another branch,
opening another pull request, or deleting any branch.

## Local Checkout Safety

Some local workspaces may have a `main` branch that was created before this
repository was connected to `gwonxhj/InferEdge`. If local `main` has unrelated
history, do not use it as the base for new work and do not force push it over
the public `main` branch.

The readiness check prints `Local main safety: review before publishing` when
the current branch is `main` but it is not tracking `origin/main`. Treat that as
a prompt to stop and start from `origin/main`, not as a reason to repair the
history with force push or `--allow-unrelated-histories`.

For new work, use the remote-tracking branch directly:

```bash
git fetch origin main
git switch -c codex/<next-task> origin/main
```

Only repoint or delete a stale local `main` after confirming the working tree is
clean and no local-only commits need to be preserved. Until then, treat
`origin/main` as the source of truth for new InferEdge entrypoint branches.

## After PR Merge

After a pull request is merged, fetch `main` and verify the merge commit before
starting more work:

```bash
git fetch origin main
git log --oneline -3 origin/main
```

It is fine for the local checkout to remain on the merged feature branch. Do
not run `git pull` into a stale or unrelated local `main`. Start the next task
from `origin/main` instead:

```bash
git switch -c codex/<next-task> origin/main
```

If you accidentally switch to a stale local `main` and
`git merge --ff-only origin/main` reports
`fatal: refusing to merge unrelated histories`, stop there. Do not retry with
`--allow-unrelated-histories`, force reset, or force push as a routine publish
step. Switch back to a clean review branch or create a fresh branch from
`origin/main`; only repoint local `main` after separately confirming no
local-only commits need to be preserved.

If `git status --short --branch` on the stale local `main` shows normal repo
paths as `??` untracked files, treat that as a checkout mismatch signal. Do not
delete those apparent untracked files with `rm`, `git clean`, or similar cleanup
commands. Leave the stale `main`, return to the previous review branch or create
a fresh branch from `origin/main`, and verify the working tree there:

```bash
git switch -
# or:
git switch -c codex/<next-task> origin/main
git status --short --branch
```

Delete merged local or remote branches only when you are sure they are no
longer needed for review or audit.

## Optional Branch Cleanup

Branch cleanup is optional. Keep merged branches if they are still useful for
review, audit, or comparing local logs. Never delete `main`.

Before deleting anything, make a cleanup inventory and treat it as audit input,
not a deletion list:

```bash
bash scripts/audit_branch_cleanup.sh --fetch
```

The audit script lists local `codex/*` branches, matching `origin/codex/*`
remote branches, and the local subset that appears in regular merge ancestry.
Those entries are cleanup inventory only. The ancestry subset only proves
regular merge ancestry; it is not sufficient for squash-merged pull requests,
so the audit output is still not a deletion list. If the audit summary reports
zero regular-merge ancestry entries, that does not mean there are zero
squash-merged PR branches; use the PR merged state as the deciding evidence.

Use this merged PR confirmation checklist before deleting any local or remote
branch:

1. Match the branch name to its GitHub pull request.
2. Confirm the pull request is closed as merged, not merely closed.
3. Confirm the merge commit is visible on the current `origin/main`.
4. Confirm the branch is no longer needed for review, audit, or comparing local
   logs.
5. Keep the branch when any of those checks is uncertain.

Before deleting a local branch, verify it is merged into the current
`origin/main`:

```bash
git fetch origin main
git branch --merged origin/main
git branch -d codex/<merged-topic>
```

Before deleting a remote branch, verify the pull request is merged and the
merge commit is present on `origin/main`:

```bash
git log --oneline -3 origin/main
git push origin --delete codex/<merged-topic>
```

If a branch is not listed by `git branch --merged origin/main`, stop and inspect
the branch before deleting it.

Squash-merged branches may not appear in `git branch --merged origin/main`
because their branch commits were copied into new commits on `main`. In that
case, do not delete the branch based on `--merged` alone. Verify the PR is
closed as merged and keep the branch if review or audit context is still useful.
When the local `gh` token is invalid, use the authenticated GitHub connector/app
or GitHub PR page to confirm the PR merged state before deleting any local or
remote branch.

## Blocked States

If the check reports `Origin reachability: failed`, the URL points to a
repository that does not exist or that your authenticated GitHub account cannot
access. Create the repository first or replace `origin` with the correct URL.

`Origin branch state: publishable` is the only normal remote branch state for a
direct push to the current branch. It means `origin/<branch>` is already an
ancestor of the local branch and a normal push can update the remote without
rewriting history.

If the check reports `Origin branch state: unrelated-history`, `local-behind`,
or `diverged`, the remote branch already contains commits that cannot be
updated by a normal fast-forward push. Do not force push; integrate the remote
history first, push a separate review branch, or choose an empty repository
intended for the new history.

If `origin` is missing, add the intended remote URL:

```bash
REMOTE_URL="<paste-real-git-remote-url-here>"
git remote add origin "$REMOTE_URL"
```

Replace the entire value inside quotes with the real repository URL before
running the command. Do not type unquoted angle-bracket placeholders such as
`<remote-url>` into zsh; `<` is parsed as shell redirection.

The `--allow-dirty`, `--allow-missing-remote`,
`--allow-placeholder-remote`, and `--skip-remote-check` flags are diagnostic
escape hatches. Do not use them for normal branch publish or PR merge flow,
because they can bypass the blocked-state evidence that protects `main`.

## Notes

- Do not publish if any validation smoke fails.
- Do not commit generated sibling `reports/` folders unless a fixture
  explicitly requires them.
- A missing `origin`, placeholder `origin`, unreachable `origin`, or unrelated
  existing `origin/main` is a blocked publish state.
- Jetson hardware is not required for the publish readiness check.
