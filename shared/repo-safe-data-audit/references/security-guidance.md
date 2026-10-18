# Security guidance for repository data audits

Use this reference when evaluating secret findings, Git history, and prevention. The skill links primary sources so the guidance can be rechecked as tools and hosting behavior change.

## Secret scanning

Run a local scanner over both the working tree and the locally available Git history. Gitleaks supports directory and Git modes and has a full-redaction option; check `gitleaks --help` for the installed release because command names and flags can change. Do not assume one scanner finds every credential: provider patterns, entropy rules, generic passwords, private keys, and custom token formats have different coverage. A second detector can add coverage, but its reports and baselines may themselves include sensitive paths or values; keep them local and inspect output modes before use.

Treat findings as leads, not proof of validity. Never validate a suspected credential by attempting to log into a service. Disable scanner/provider online validity checks. Plan rotation or revocation with its owner/provider if it may be real; the audit itself never changes credentials. Do not include the value or a partial value in reports, terminal output, tickets, or commits. Console redaction does not guarantee that every report field or snippet is redacted: normalize findings to type/location/commit/status before reading them into a model context. Do not retain credential-derived hashes in the plan.

Local scanning does not establish remote cleanliness. Scanning remote hosting through its API or web interface requires separate authorization and may expose content to that provider's systems. Hosted secret scanning and push protection have plan, provider-pattern, and feature limits; they supplement local controls rather than replace privacy review.

## Git history and exposure

`.gitignore` prevents eligible untracked paths from being added by common workflows; it does not remove already tracked files. Removing a file in a later commit leaves prior blobs in history. Rewriting refs changes commit identities and can disrupt branches, tags, signatures, pull requests, and collaborators. Old clones, forks, cached views, CI artifacts, releases, or service backups may still hold prior objects. Coordinate history cleanup and request hosting-provider help where necessary; do not claim complete deletion based only on a successful force push.

A new repository with a deliberately constructed initial commit can provide a clean project history for future work. It does not itself delete the old repository or copies. The migration plan must separately specify how to retire or clearly decommission the old remote, prevent it from remaining the active push target, and handle old clones. The user performs repository creation, deletion, rewriting, settings changes, and pushes manually after reviewing the plan.

Check commit messages and metadata separately when a scanner scans only patches.
Distinguish reachable branch/tag/ref history, stash/reflog and missing objects.
A shallow clone, submodules, LFS pointers without payloads, inaccessible archives,
binary files and repository-configured allowlists are explicit coverage gaps.
Do not run Git textconv/external diff commands or scanner plugins from the audited
repository. Use bounded archive inspection and do not follow links outside scope.

## Prevention and verification

Use layered local controls: explicit staging, staged-diff review, a local secret scanner before commit/push, appropriate ignore rules, synthetic test fixtures, and optional host push protection when available. A pre-commit hook can be bypassed and may not be installed by every clone; document setup and keep CI or push protection as additional checks where compatible with the privacy goal.

For a clean initial commit, validate the exact index and commit tree against an explicit allowlist of neutral skeleton paths. Scan the staged tree and the complete new local history. Then, as a separately authorized manual operation, inspect the new remote's default branch and refs to confirm the expected initial commit and absence of prior history. Keep scan reports outside the repository and redact findings.

## Optional local language models

A local language model can assist with low-confidence classification of filenames, directory structure, or excerpts only after deterministic secret scanning and redaction. Keep this feature opt-in. Verify the runtime, model identity, and local endpoint before sending even sanitized project metadata; prefer loopback, and do not treat an OpenAI-compatible API as proof that the service is local. Never send credentials, raw scanner output, or unreviewed full repository text. Do not use a model to validate credentials, waive findings, determine legal publication rights, or authorize pushing. Keep prompts and outputs local, minimize input, and treat model output as a suggestion requiring human review. If locality is uncertain or no runtime is available, skip the model step.

## Primary references

- [GitHub: Removing sensitive data from a repository](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)
- [git-filter-repo sensitive-data removal documentation](https://github.com/newren/git-filter-repo/blob/main/Documentation/git-filter-repo.txt)
- [Gitleaks documentation and repository](https://github.com/gitleaks/gitleaks)
- [Yelp detect-secrets repository](https://github.com/Yelp/detect-secrets)
- [GitHub: Supported secret scanning patterns](https://docs.github.com/en/code-security/reference/secret-security/supported-secret-scanning-patterns)
- [GitHub: Enabling push protection](https://docs.github.com/en/code-security/how-tos/secure-your-secrets/prevent-future-leaks/enable-push-protection)
