# Implementation plan contract

The audit's product is a private saved plan, not executed migration. Write in the
user's language. Replace generic headings with repository-specific evidence,
exact paths and decisions; unknowns must remain visibly unresolved. Do not copy
secret values, snippets or credential fingerprints into artifacts or chat.

## Required files

`IMPLEMENTATION-PLAN.md` must exist in a unique private artifact directory outside
Git. Include an inventory JSON in the same directory when needed to cover every
tracked path without a giant document. Both are sensitive and stay local.
Relative links between plan/evidence are allowed; links into the audited repo
must name exact paths and line/commit locators. Save incomplete audits too, with
status INCOMPLETE, precise missing coverage and the next reproducible checks.

## Required contents

1. **Decision and scope.** Recommended route, reasons, target threat model (what
   can be inferred from remote), acceptable disclosure boundaries and residual
   risks. Snapshot HEAD, refs inspected, dirty/staged/untracked state and audit
   date. Distinguish observations from estimates and inference. Do not print
   remote URLs with userinfo, query tokens or private service addresses in chat.
2. **Coverage.** File/ref counts, sizes, scanner versions/config/modes and limits,
   scan exits (findings versus tool errors), missing objects/refs, shallow/partial
   status, uninspected binaries/archives/LFS and inaccessible host-side surfaces.
   Offline verification status of credentials is UNKNOWN, never 'inactive'.
3. **Findings.** Stable finding ID, severity and confidence, category, safe file/
   line/commit locator, effect, recommended remedy and evidence source. Clearly
   distinguish suspected credentials, confirmed secret material and ordinary
   privacy/data exposure. Do not claim a live token merely from its pattern.
4. **Exhaustive disposition map.** For every current tracked path, specify KEEP,
   LOCAL, GENERALIZE or REVIEW. Group only with explicit complete path lists or
   a fully expanded inventory plus exclusion precedence. Include target path,
   why, dependencies, count/size and evidence. No unclassified paths; REVIEW
   blocks publication until resolved. Add relevant ignored/untracked data scope
   for preservation/backups without scanning unrelated directories.
5. **Architecture and data contract.** Exact future directory trees, configured
   data-root precedence, path resolution/validation rules, symlink behavior,
   missing-input errors, neutral schemas/templates, and compatibility with local
   workflows. Specify which script functions/CLI entrypoints and docs change.
6. **History/remote decision.** Compare rewrite and clean-new-repo routes. Explain
   old host copies and the limits of deletion. Recommend a neutral repo name only
   if asked; otherwise use an explicit neutral placeholder. List host, forks,
   clones, PR/issue/wiki/pages/release/LFS/CI checks that require manual inspection.
7. **Backup design.** Exact scope/exclusions and dependencies, daily scheduler for
   the detected OS, catch-up behavior, environment variable names (no values),
   SFTP server assumptions and unresolved settings, host-key provisioning,
   integrity and restore checks, at-rest encryption/key recovery choice, lock,
   logs, failures, retention of five complete restore points, staging/pruning
   order, free-space needs and an isolated restore drill. Never prune the last
   good copy on scan/upload/verification failure or treat a partial upload as a
   version. Do not remove chunks referenced by retained incremental backups.
8. **Prevention.** Explicit skeleton allowlist and tests for unknown additions;
   ignore rules are secondary. Local staged-tree secret scan and content/privacy
   checks before publishing, synthetic fixtures, pre-commit/pre-push limitations
   and optional hosted protections with availability unverified until checked.
9. **Task cards.** Each card must contain:

   | Field | Required detail |
   |---|---|
   | ID/dependencies | Stable task ID; predecessor cards and blockers |
   | Exact scope | Files/functions to edit, create or retire; before/after paths |
   | Implementation | Concrete behavior or patch specification, no architecture guesswork |
   | Commands | Correct shell, cwd, bounded paths; no real secrets or executable interpolation |
   | Invariants | Which data, identifiers, hashes, local changes and workflows must survive |
   | Validation | Observable checks with expected success and failure outcomes |
   | Stop conditions | Missing permission, collision, changed HEAD, bad hash, unknown secret finding |
   | Rollback | How to return to checkpoint without overwriting work or re-publishing data |
   | Executor | Model/local work or HUMAN ONLY for remote lifecycle and publication |

10. **Acceptance and handoff.** Self-contained prompt for SOL 6.1 medium naming
    the saved plan, scope, task order, blocked cards, commands, allowed local
    changes and explicit requirement to stop before human-only actions. Do not
    imply the present audit authorizes applying the plan. State what has actually
    been verified and what the implementer must revalidate if HEAD/files changed.

## Required migration checkpoints

- C0: record local state and establish a verified private backup, including dirty
  files and any needed local history. Neither delete nor replace the old tree.
- C1: prepare separate neutral skeleton from an explicit reviewed allowlist; avoid
  blanket copying, `git add .`, old `.git` and inherited hooks/submodules.
- C2: apply exact code/config edits; test synthetic fixtures and restoration of
  local workflows. Do not send real private data into hosted CI or model prompts.
- C3: scan exact candidate tree, build artifacts and all new commits, inspect
  metadata and inventory. Every REVIEW and secret finding must be resolved.
- C4: establish SFTP backup and run isolated restore verification in a later
  authorized implementation phase before removing any existing recovery route.
- C5 HUMAN ONLY: review final tree, choose whether to delete/recreate the old
  remote or create another, verify host-side effects and recovery implications,
  create clean initial history and publish manually. No force/mirror pushes from
  the old clone; never remove a remote while backup/validation is incomplete.
- C6 HUMAN ONLY: fresh clone from intended new URL; verify expected root commit,
  complete ref inventory, no old ancestry, allowed tree only, repeated secret and
  privacy checks, old-clone push targets disabled, and old host surfaces addressed.

Remote deletion is irreversible for the workflow even if a host offers recovery.
The plan may describe this user-approved option but must never say it guarantees
erasure of third-party clones, caches, forks or retained service backups.
