# Contributing to Republic of Rome Online

Republic of Rome Online is a free, non-commercial hobby project. Contributions are welcome.

## Getting started

- [How it works](docs/how-it-works.md) — architecture overview for new contributors
- [Setup a development environment](docs/setup-development-environment.md) — get the project running locally
- [Infrastructure](docs/infrastructure.md) — production deployment details

## Reference

- [Rule interpretations](docs/rule-interpretations.md) — how ambiguous rules are handled
- [Terminology changes](docs/terminology-changes.md) — vocabulary that differs from the original game
- [Orthographic guidelines](docs/orthography.md) — spelling and capitalization conventions

## Issues

Bug reports and feature suggestions are welcome via [GitHub Issues](https://github.com/iamlogand/republic-of-rome-online/issues).

Each issue should track one thing. If an issue covers multiple problems or tasks, split them into separate issues. If they're related, use GitHub's sub-issue feature to group them under a parent issue.

## Pull requests

Each PR should resolve just one issue. If a change solves multiple issues, consider splitting it into separate PRs.

Try to keep pull requests under 400 lines changed. Larger PRs are fine when the work genuinely can't be split up, but smaller PRs are faster to review, easier to understand, less likely to let bugs through, and make it easier to pinpoint the cause of a regression.

Some strategies for breaking a large PR into smaller ones:

- **Separate refactoring from features** — if a feature requires restructuring existing code first, land the refactor as its own PR so the feature PR is purely additive.
- **Split by layer** — backend and frontend changes for the same feature can often be split into separate PRs, with the backend merged first.
- **Preparatory PRs** — add a new model, utility, or stub in one PR, then build on it in the next.
- **Incremental features** — ship a minimal working version first, then follow up with enhancements or edge-case handling in subsequent PRs.

PR descriptions are allowed to be short. The code itself should explain the what and the how — the description is there to summarize the PR and document the why when it can't be inferred from the code.