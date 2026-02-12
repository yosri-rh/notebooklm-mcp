# Branch Protection Rules

## Main Branch Protection

The `main` branch is protected to maintain code quality and ensure proper review processes.

### Protection Rules

✅ **Enabled:**
- ✅ Require pull request before merging
- ✅ Dismiss stale pull request approvals when new commits are pushed
- ✅ No direct pushes to main (all changes must go through PRs)
- ✅ No force pushes allowed
- ✅ No branch deletion allowed

⚠️ **Not Enforced for Admins:**
- Admins can bypass these rules if necessary (for emergency fixes)

### Workflow for Contributors

All changes to `main` must follow this workflow:

```bash
# 1. Create a feature branch
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix

# 2. Make your changes and commit
git add .
git commit -m "feat: your change description"

# 3. Push your branch
git push -u origin feature/your-feature-name

# 4. Create a pull request
gh pr create --base main --head feature/your-feature-name \
  --title "Your PR Title" \
  --body "Description of changes"

# 5. Wait for review (if required)
# 6. Merge the PR (via GitHub UI or gh CLI)
gh pr merge <PR-number> --squash

# 7. Pull the updated main branch
git checkout main
git pull origin main

# 8. Delete your feature branch
git branch -d feature/your-feature-name
git push origin --delete feature/your-feature-name
```

### Direct Push Behavior

Attempting to push directly to `main` will result in an error:

```bash
$ git push origin main
remote: error: GH006: Protected branch update failed for refs/heads/main.
remote: error: Changes must be made through a pull request.
```

### Emergency Fixes

For critical emergency fixes, repository admins can:
1. Temporarily disable branch protection
2. Make the fix directly
3. Re-enable branch protection

Or better yet, create a quick PR and merge immediately without waiting for review.

### Checking Protection Status

```bash
# View current protection settings
gh api repos/yosri-rh/notebooklm-mcp/branches/main/protection

# Or visit GitHub Settings
# https://github.com/yosri-rh/notebooklm-mcp/settings/branches
```

## Benefits

1. **Code Quality** - All changes reviewed before merging
2. **History Preservation** - No force pushes or accidental deletions
3. **Collaboration** - Encourages discussion and review
4. **Audit Trail** - Clear record of all changes via PRs
5. **CI/CD Integration** - Can require status checks to pass

## Related Documentation

- [CONTRIBUTING.md](../docs/CONTRIBUTING.md) - Contribution guidelines
- [GitHub Branch Protection Docs](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
