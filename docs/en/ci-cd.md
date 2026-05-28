# CI/CD

## Description

DNS Orchestration uses a fully automated CI/CD pipeline based on GitHub Actions.

The system follows a continuous release model, where each commit on main can generate a new stable system version.



## Release model

Versioning is handled automatically using SemVer:

* Each commit on main triggers a version analysis
* Commits are reviewed from the last existing tag
* A new version is calculated automatically
* A Git tag is created (vX.Y.Z)
* A Docker image is built and published
* The latest tag is updated

## Versioning strategy

- `feat:` → minor version increase
- `fix:` → patch version increase
- `BREAKING CHANGE` → major version increase

Example:

* v1.0.0 → feat → v1.1.0
* v1.1.0 → fix → v1.1.1
* v1.1.1 → BREAKING CHANGE → v2.0.0

## Release flow (main pipeline)

When a push is made to main:

1. The workflow is triggered automatically
2. The latest existing tag is retrieved
3. If a previous tag exists:
    * commits from that tag to HEAD are used
4. If no tag exists:
    * v0.0.0 is used as the internal base version
    * all repository commits are analyzed
5. A new SemVer version is calculated
6. A Git tag is created
7. The multi-arch Docker image is built
8. The image is published to GHCR
9. latest is updated with the same build

## Bootstrap (first release)

When no tags exist in the system:

* no previous version reference is available
* v0.0.0 is used as the base version
* the full commit history is used for calculation
* the first tag is generated automatically
* the first Docker image is published
* latest points to that build

This behavior occurs only once.

## Docker publishing

Each release generates:

* vX.Y.Z
* latest (always points to the latest stable build)

## Branch strategy

The repository is organized into two main branches:

### main → Production

* contains the stable system state
* each commit can generate an automatic release
* triggers full CI/CD pipeline:
    * SemVer versioning
    * tag creation
    * Docker image build
    * GHCR publishing
    * latest update
* represents the deployable production state

---

### develop → Development

* integration branch for new features
* does not generate releases
* may contain incomplete or experimental changes
* used to prepare changes before merging into main

---

### Promotion flow

* feature branches → merged into develop
* develop → stabilized
* develop → merged into main → triggers release

## Important notes

* tags are not created manually
* versioning is fully automated
* commit history defines the system version
* main always represents the stable deployable state

## Commit convention

* feat: new feature
* fix: bug fix
* BREAKING CHANGE: incompatible change