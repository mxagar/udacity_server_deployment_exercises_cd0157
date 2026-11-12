# Reviewer notes: Deploy Your Flask App to Kubernetes Using EKS

This submission provides a Flask JWT API deployed on EKS through a GitHub-triggered CodePipeline/CodeBuild workflow. The implementation, live verification results, and declared differences from the historical course instructions are summarized below.

## Changes addressing review feedback

- The Dockerfile now literally uses `FROM python:stretch`, installs pinned dependencies from `requirements.txt` with pip, and retains the exact required Gunicorn entry point. The image's Python 3.7.4 runtime passes all 14 regression tests.
- [.env.example](./.env.example) is included as the file-based local configuration template. The [README's local setup](./README.md#create-the-local-environment-file) explains creating a private `.env`, generating a local signing secret, and starting Docker with `--env-file .env`. No production secret is included. Missing or empty `JWT_SECRET` now causes a clear startup error instead of using a fallback.
- CodeBuild tests both its host environment and the actual Stretch container before publishing. The extra startup tests cover missing, empty, and explicitly configured secrets.
- The internet-facing ELB passed health, auth, contents, and missing/invalid-token checks on **2026-11-12 at 13:04:57 Europe/Budapest** after the revised image deployed. The [fresh cloud evidence](./evidence/resubmission-2026-11-12.json) records the successful run; the original 2026-11-11 gate evidence is retained as history.
- No video recording is provided. The rubric reproduced in the project guide requires endpoint behavior and deployment evidence, but does not list a recording requirement; verification uses the live API and linked logs/results.

## Implementation and live API

- Repository: https://github.com/mxagar/udacity_server_deployment_exercises_cd0157
- Branch: `master`.
- Verified/deployed application commit: `4d4fe962a89eb097f4ef0406a26d81e3b8ee4e47`.
- AWS region: `eu-central-1`.
- API base URL: http://a801c89a3b3334c9aa490f41d56834f7-6753305.eu-central-1.elb.amazonaws.com
- The load balancer exposes **HTTP on port 80**. Keep the explicit `http://` scheme when opening or testing it; an HTTPS-only client needs to permit this course endpoint's HTTP connection.
- Verification date: 2026-11-12. The recorded cloud results correspond to the application commit above; subsequent documentation/evidence commits do not change application behavior.
- Successful resubmission pipeline: `89cb1262-70a2-42ca-bb1d-be7366e08f92`.
- Successful resubmission CodeBuild run: `simple-jwt-api-pipeline:46c4b34e-2c97-4331-a85a-b6a925a2c0bc`.

To verify the live API:

1. `GET /` returns the JSON string `"Healthy"`.
2. `POST /auth` with nonempty `email` and `password` JSON fields returns a JWT. Example body: `{"email":"reviewer@example.com","password":"exercise-only"}`.
3. `GET /contents` with `Authorization: Bearer <that token>` returns verified `email`, `exp`, and `nbf` claims.
4. Missing or invalid tokens return 401. Reviewers can issue their own exercise token without the signing secret; the starter checks field presence rather than authenticating against a user database.

For local reproduction, create a private `.env` from [.env.example](./.env.example), replace its placeholder with your own random local secret, then run the following from the repository root. The full Bash/PowerShell file-setup instructions are in the [README](./README.md#create-the-local-environment-file).

```text
# Bash or PowerShell
docker build -t simple-flask-project .
docker run --rm --env-file .env -p 127.0.0.1:8080:8080 simple-flask-project
```

Use `http://127.0.0.1:8080` for those local endpoint checks. No real production secret is included in the repository or archive.

## Evidence included in this repository

The evidence files were **moved from the companion deployment guide into this repository's `evidence/` directory** so the source and cloud test-gate results can be reviewed together. The relative links below point to the submitted snapshots.

| File | What it demonstrates |
| --- | --- |
| [evidence/resubmission-2026-11-12.json](./evidence/resubmission-2026-11-12.json) | Revised Stretch/pip image deployed successfully; 14 host and 14 Python 3.7.4 container tests, three ready replicas, and timestamped live ELB/API/401 checks. |
| [evidence/resubmission-runtime-tests.txt](./evidence/resubmission-runtime-tests.txt) | Local regression output showing all 14 tests pass inside the actual Python 3.7.4 Stretch image. |
| [evidence/resubmission-local-checks.json](./evidence/resubmission-local-checks.json) | Revised local Gunicorn container endpoint checks using a privately supplied `.env`. |
| [evidence/baseline.json](./evidence/baseline.json) | Healthy initial deployment, three ready replicas, original image/revision/Pod IDs, and ECR image metadata before the intentional failure. |
| [evidence/failed-run.json](./evidence/failed-run.json) | Intentional pytest failure; no image publication or deployment; ECR tags/digests, running image/revision, and Pods remained unchanged. |
| [evidence/restored-run.json](./evidence/restored-run.json) | Corrected successful pipeline/build, 11 passing tests, image publication, completed rollout, three updated/ready replicas, and live endpoint/401 checks. |

The snapshots contain selected build-log messages and before/after deployment checks. The current suite contains 14 tests; the original three 2026-11-11 snapshots refer to the earlier 11-test gate demonstration. The detailed command history is retained in the companion guide's project README.

## Evidence safety and disclosed metadata

The evidence JSON and selected runtime-test output were checked for secrets and contain **no signing-secret values, bearer JWTs, AWS credentials, GitHub tokens, or private keys**. Only selected build logs and verification metadata are included.

The snapshots disclose the AWS account ID, region, ECR/resource names, image tags/digests, execution and Pod IDs, timestamps, and public API URL to make the results traceable. These identifiers do not grant access by themselves. AWS classifies [account IDs](https://docs.aws.amazon.com/accounts/latest/reference/manage-acct-identifiers.html) and [ARNs](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference-arns.html) as identifiers rather than secrets.

The local `.env`, signing secret, decrypted Parameter Store values, and raw Kubernetes Secret payloads are excluded from the evidence. AWS credentials and the signing secret are not needed to exercise the public API: `/auth` issues a fresh exercise token for the reviewer's requests.

## Original test-gate demonstration — 2026-11-11

| Item | Intentional failure | Restored passing suite |
| --- | --- | --- |
| Commit | `d01c8400093f7a11ba43112d6b20ee62eca91dc5` | `7c9bf6e79b512fe32ccd2cf5e187e2d6f92b9f34` |
| Pipeline execution | `8dfc1287-f54e-4bce-af0d-63ebe861a0fd` — Failed | `b3de9dbe-67cb-4e3f-89bd-4580d985e652` — Succeeded |
| CodeBuild run | `simple-jwt-api-pipeline:f7ce2d8b-cd12-44a3-918b-49214350f96f` | `simple-jwt-api-pipeline:98bb9388-2e29-4b3c-a0f9-7ed56e4f0e65` |
| Tests | 1 intentional failure, 10 passed | 11 passed |

Both pushes automatically triggered CodePipeline. The temporary failing assertion was removed; the final source is passing. `buildspec.yml` runs pytest before image build and places the `CODEBUILD_BUILD_SUCCEEDING` guard before publication/deployment in `post_build`.

## Rubric alignment and runtime notes

- **Docker requirements now match the literal rubric:** `FROM python:stretch`; pip installation from `requirements.txt`; entry point `["gunicorn", "-b", ":8080", "main:APP"]`. The previous `python:3.13-slim`/uv-in-Docker substitutions have been removed.
- **Pinned compatibility dependencies:** Flask 2.2.5, PyJWT 2.8.0, and Gunicorn 23.0.0 support the historical Python 3.7.4 runtime. `requirements.txt` and `requirements-dev.txt` are exported from `uv.lock`; host tooling can still use Python 3.13/uv. CodeBuild runs the 14-case suite in both environments, including inside the real runtime image.
- **Legacy scope:** Debian Stretch and Python 3.7 are end-of-life. They are used here specifically to satisfy the course's historical Docker requirement, rather than as a current production-runtime recommendation.
- **AWS settings:** AWS CLI v2, EKS 1.37, kubectl 1.37.2, and CodeBuild `aws/codebuild/standard:8.0` are used in `eu-central-1`. The required API and GitHub → CodePipeline → CodeBuild → ECR → EKS flow remain intact.
- **Local names:** `.env`, image `simple-flask-project`, and container `simple-flask-container` replace illustrative names.
- **Additions:** Kubernetes Secret delivery, HTTP readiness checks, the failed-build publication guard, and rollout verification support the required deployment behavior. Optional extra API endpoints and custom failure alerts were not implemented.
