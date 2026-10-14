---
name: conventional-commit-messages
description: Use when composing, reviewing, or validating Conventional Commit messages, choosing commit types or scopes, preparing a commit, or executing git commit in a workspace.
---

# Conventional Commit Messages

## When to Use

- Write or review a commit message using Conventional Commits.
- Decide the type, scope, body, or footer for a change.
- The user asks to create a commit.

## Rules

Use one of these header formats:

```text
<type>: <subject>
<type>(<scope>): <subject>
<type>!: <subject>
<type>(<scope>)!: <subject>
```

The scope is optional. For a breaking change, append `!` after the type or scope and before the colon.

Use these types by default:

| Type | Use for |
| --- | --- |
| `feat` | A user-visible feature |
| `fix` | A bug fix |
| `docs` | Documentation only |
| `style` | Formatting or stylistic changes without behavior changes |
| `refactor` | Code restructuring without behavior changes |
| `perf` | A performance improvement |
| `test` | Adding or changing tests |
| `build` | Build system or dependency changes |
| `ci` | CI configuration or automation |
| `chore` | Maintenance not covered by another type |
| `revert` | Reverting an earlier commit |

Use another type only when the change does not fit these categories; explain the reason and use the type consistently.

Write the subject in English as an imperative phrase. Keep the entire header, including type and scope, to 72 characters or fewer. Do not end it with a period.

Use an optional, lowercase module name as the scope, such as `cli` or `parser`. Omit the scope when the change spans multiple modules or no clear module applies.

When staging all changes brings together multiple independent purposes, choose the type for the primary impact, omit the scope, and use the body to mention other included changes. If there is no clear primary purpose, stop and ask before committing.

Every commit message must include a concise body in Traditional Chinese. State the intent, context, or impact without merely repeating the subject. Add a blank line before the body.

Add issue references only when the issue is known: `Refs #123` for a related issue or `Closes #123` when the commit closes it. Do not invent issue numbers or relationships.

For a breaking change, include both the `!` marker in the header and a footer after the body. Start the footer with `BREAKING CHANGE:` and describe the compatibility impact and migration action in Traditional Chinese.

Example:

```text
feat(api)!: require an account ID for requests

請求現在必須提供帳戶 ID；未提供時會回傳 400，呼叫端需在升級前補上此欄位。

BREAKING CHANGE: 未提供 accountId 的請求不再成功處理。請先更新所有呼叫端，再升級此版本。
```

## Procedure

1. Determine whether the user wants a message draft or an actual commit. If they only ask for a message, return one copy-ready draft in a fenced code block and do not run Git commands that stage, commit, or push. Include the required body unless they specifically ask for only a subject or header.
2. For a commit, inspect the current branch, all tracked and untracked changes, and the complete diffs before choosing a message. Base the type and subject on the actual changes; if multiple purposes have no clear primary purpose, or the intent cannot be determined, ask before committing.
3. If a diff contains an apparent password, access token, private key, or other credential, stop before staging or committing and ask the user how to handle it.
4. When the user explicitly asks to commit, stage all changes, including unrelated changes and untracked files, with `git add -A`. Review the staged diff before proceeding.
5. Run tests only when repository instructions or the user require them. If tests are run and fail, stop without committing and report the failure. Report any required tests that could not be run.
6. Create a message that follows every rule above, then create a new commit. Do not amend or rewrite existing commits unless explicitly requested.
7. Verify the new commit and remaining working-tree changes. Report the commit hash, message, test status, and whether changes remain.

Never push automatically. Push only when the user explicitly asks for it. A request to commit does not imply a request to push.