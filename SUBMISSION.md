# Submission: Deploy Your Flask App to Kubernetes Using EKS

## Implementation and live API

- Repository: https://github.com/mxagar/udacity_server_deployment_exercises_cd0157
- Branch: `master`.
- Verified/deployed application commit: `7c9bf6e79b512fe32ccd2cf5e187e2d6f92b9f34`.
- AWS region: `eu-central-1`.
- API base URL: http://a801c89a3b3334c9aa490f41d56834f7-6753305.eu-central-1.elb.amazonaws.com
- Verification date: 2026-11-11. The evidence records this application commit; a later documentation-only commit may contain this submission file and the evidence.

Reviewer checks:

1. `GET /` returns the JSON string `"Healthy"`.
2. `POST /auth` with nonempty `email` and `password` JSON fields returns a JWT.
3. `GET /contents` with `Authorization: Bearer <that token>` returns verified `email`, `exp`, and `nbf` claims.
4. Missing or invalid tokens return 401. Reviewers can issue their own exercise token without the signing secret; the starter checks field presence rather than authenticating against a user database.

## Evidence included in this repository

The evidence files were **moved from the parent deployment guide into this repository's `evidence/` directory**, so the application source and test-gate evidence can be reviewed together. Include this file and the evidence directory when committing/pushing the submission or preparing a ZIP.

| File | What it demonstrates |
| --- | --- |
| [evidence/baseline.json](./evidence/baseline.json) | Healthy initial deployment, three ready replicas, original image/revision/Pod IDs, and ECR image metadata before the intentional failure. |
| [evidence/failed-run.json](./evidence/failed-run.json) | Intentional pytest failure; no image publication or deployment; ECR tags/digests, running image/revision, and Pods remained unchanged. |
| [evidence/restored-run.json](./evidence/restored-run.json) | Corrected successful pipeline/build, 11 passing tests, image publication, completed rollout, three updated/ready replicas, and live endpoint/401 checks. |

The parent guide's project README retains the fuller activity and command log. The three snapshots here are the portable cloud demonstration evidence; add any separate local-build captures or screenshots required by the course's submission form.

## Evidence safety and disclosed metadata

The three current JSON files were inspected on 2026-11-11 and contain **no signing-secret values, bearer JWTs, AWS credentials, GitHub tokens, or private keys**. They contain selected build logs and verification metadata and are suitable to commit for review.

They disclose the AWS account ID, region, ECR/resource names, image tags/digests, execution and Pod IDs, timestamps, and the intended public API URL. These identifiers describe the deployment and do not grant access by themselves. AWS classifies [account IDs](https://docs.aws.amazon.com/accounts/latest/reference/manage-acct-identifiers.html) and [ARNs](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference-arns.html) as identifiers rather than secrets. Public publication makes that infrastructure metadata visible; private reviewer-accessible attachments are an alternative if that visibility is undesirable.

Keep `.env`, signing secrets, decrypted Parameter Store output, raw Kubernetes Secret values/base64 payloads, and unreviewed full logs out of Git. This review applies to these three snapshots, not automatically to future evidence or the repository's entire history. Reviewers do not need AWS credentials or the signing secret to exercise the public API.

## Test-gate demonstration

| Item | Intentional failure | Restored passing suite |
| --- | --- | --- |
| Commit | `d01c8400093f7a11ba43112d6b20ee62eca91dc5` | `7c9bf6e79b512fe32ccd2cf5e187e2d6f92b9f34` |
| Pipeline execution | `8dfc1287-f54e-4bce-af0d-63ebe861a0fd` — Failed | `b3de9dbe-67cb-4e3f-89bd-4580d985e652` — Succeeded |
| CodeBuild run | `simple-jwt-api-pipeline:f7ce2d8b-cd12-44a3-918b-49214350f96f` | `simple-jwt-api-pipeline:98bb9388-2e29-4b3c-a0f9-7ed56e4f0e65` |
| Tests | 1 intentional failure, 10 passed | 11 passed |

Both pushes automatically triggered CodePipeline. The temporary failing assertion was removed; the final source is passing. `buildspec.yml` runs pytest before image build and places the `CODEBUILD_BUILD_SUCCEEDING` guard before publication/deployment in `post_build`.

## Declared differences from the historical rubric

- **Base-image substitution:** `python:3.13-slim` replaces the original rubric's `python:stretch`. The exact Gunicorn entry point `["gunicorn", "-b", ":8080", "main:APP"]` is preserved, dependencies install, and the required endpoint checks pass. Please evaluate this declared version substitution against the historical rubric; this note does not claim a waiver.
- **Dependencies:** Python 3.13 with `pyproject.toml`, `uv.lock`, and uv replaces the older pip/`requirements.txt` workflow. Docker installs locked runtime dependencies; CodeBuild installs pytest and runs `uv run --locked python -m pytest test_main.py`.
- **Compatibility updates:** current Flask/PyJWT APIs, AWS CLI v2, EKS 1.37, kubectl 1.37.2, and CodeBuild `aws/codebuild/standard:8.0` are used in `eu-central-1`. The required API and GitHub → CodePipeline → CodeBuild → ECR → EKS flow remain intact.
- **Local names:** `.env`, image `simple-flask-project`, and container `simple-flask-container` replace illustrative names.
- **Additions:** Kubernetes Secret delivery, HTTP readiness checks, the failed-build publication guard, and rollout verification support the required deployment behavior. Optional extra API endpoints and custom failure alerts were not implemented.

Keep the EKS application available through review and any required resubmission, then follow the deployment guide's cleanup instructions.
