# Recovering curator-deleted skills (this host)

The Hermes curator can DELETE agent-created skills with `archived: false`
(`hermes curator list-archived` shows nothing, `hermes curator restore <name>`
cannot help). The file contents survive in content-addressed blobs, so
recovery is deterministic.

## Diagnose
```bash
P=~/.hermes/profiles/<profile>
bash $P/bin/agent-stack-doctor.sh            # which skills report MISSING
grep -a '"action": "delete"' $P/skills/.curator_ledger.jsonl | tail   # who/when/what
```
Each delete entry carries `before: [{path, sha256}, ...]` — the full manifest
of every file the skill had.

## Restore (verify hashes, never blindly copy)
Python recipe, run from the profile dir:
- Parse `skills/.curator_ledger.jsonl`; for the target skills take the LAST
  delete entry's `before[]` list.
- For each {path, sha256}: if the path already exists, skip; else the blob is
  `.curator_backups/blobs/<sha256>` — verify
  `sha256sum <blob> == sha256`, then copy the blob to the (relativized) path,
  `chmod 755` for `.sh` files.
- Re-run `agent-stack-doctor.sh` to confirm green.

## Prevent recurrence
```bash
hermes curator pin <skill>   # one per required skill; blocks future pruning
```
`curator pin` is an approval-gated write: it can time out without an
interactive click — treat a timed-out pin as NOT done and tell the user,
don't assume the combo is safe.

## Notes
- The blobs dir is shared, content-addressed: many deleted skills' files can
  be recovered the same way, not just the combo.
- This is not caused by batch installs — installs just surface it because the
  doctor compares against the expected skill set.
