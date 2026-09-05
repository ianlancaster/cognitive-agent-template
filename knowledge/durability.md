# Checkpoint durability

Use this contract for nap, sleep and deep-sleep. A completed ritual is not inferred from an idle pane.

1. Inspect the worktree and staged diff. Choose intended checkpoint files/hunks. Preserve unrelated changes and pre-staged work; a broad `git add -A` can include them even if they were previously unstaged.
2. Stage the explicit intended paths, inspect the final staged diff, and commit. If unrelated changes are already staged, use a scoped commit that excludes them and verify its diff; do not silently alter somebody else's index. If there is nothing new, identify the existing commit instead. Never claim a successful checkpoint after a failed commit.
3. Inspect the current branch's upstream. Push there when configured and authorized; do not infer a destination from an unrelated remote or push an agent's cognitive files back to its template. Report the committed revision and one backup disposition:
   - **Backed up:** push succeeded to the intended upstream.
   - **Local only:** no upstream is configured. Do not invent a remote-creation approval gate. Disclose this and continue unless an explicit backup requirement applies.
   - **Backup failed:** retain the commit and report the actual failure; do not label it backed up.
4. Before a destructive reset/teardown, follow any explicit preservation requirement. If that requirement is unmet, report the exact missing protection and preserve the session/worktree. A routine context clear is not permission to delete the repository.

For autonomous lifecycle handoffs, send `SLEEP COMPLETE` only after the intended state is durably committed (or already committed) and any explicitly required backup succeeds. Include commit, backup disposition and the resume pointer. If backup was not required, a disclosed local-only or backup-failed state can complete the ritual; it never certifies safe deletion of the only copy. Report an unmet required backup as incomplete, without entering an endless retry loop or hiding the local commit.
