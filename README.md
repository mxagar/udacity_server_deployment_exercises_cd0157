# Deploying a Flask API

Project starter for the course **Server Deployment, Containerization, and Testing**. Build and test a Flask application locally, then deploy it to Amazon Elastic Kubernetes Service (EKS) using Docker, AWS CodePipeline, and AWS CodeBuild.

## Application

| Endpoint | Behavior |
| --- | --- |
| `GET /` | Returns the JSON string `"Healthy"`; the starter also accepts `POST /`. |
| `POST /auth` | Accepts an email and password as JSON and returns a signed JSON Web Token (JWT). |
| `GET /contents` | Accepts `Authorization: Bearer <token>` and returns the verified email, expiration (`exp`), and not-before (`nbf`) claims. Invalid tokens return status 401. |

The app reads `JWT_SECRET` when imported and uses it to sign and verify tokens with HS256. Tokens are encoded, not encrypted. This exercise checks that login fields are present; it does not authenticate against a user database or include the password in the token.

Flask's development server is for local exploration. The Docker image runs the production [Gunicorn](https://gunicorn.org/) Web Server Gateway Interface (WSGI) server as `main:APP` on port 8080.

## Prerequisites

- [Docker Desktop](https://docs.docker.com/desktop/), [Git](https://git-scm.com/downloads), and an editor such as [Visual Studio Code](https://code.visualstudio.com/download).
- Python 3.13 and [uv](https://docs.astral.sh/uv/getting-started/installation/) 0.13.7 or newer. Local development, Docker, and CodeBuild use Python 3.13 and the same uv lockfile.
- A terminal: Bash on macOS/Linux or Git Bash/WSL; PowerShell is also supported below. Gunicorn runs on Windows through WSL or a Linux container.
- For cloud deployment: an AWS account, [AWS CLI v2](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html), [eksctl](https://docs.aws.amazon.com/eks/latest/eksctl/installation.html), and [kubectl](https://kubernetes.io/docs/tasks/tools/). Configure the appropriate AWS profile and keep exercise resources in a single supported region, such as `eu-central-1`.

## Initial setup and local run

The original [Udacity starter repository](https://github.com/udacity/cd0157-Server-Deployment-and-Containerization) has been forked here. For a standalone checkout:

```text
# Bash or PowerShell
git clone https://github.com/mxagar/udacity_server_deployment_exercises_cd0157.git
cd udacity_server_deployment_exercises_cd0157
uv python install 3.13
uv sync --locked
```

If this repository is already checked out as a submodule, enter that directory and start at `uv python install`. uv creates its own `.venv`; activation is unnecessary.

### Create the local environment file

The committed [.env.example](./.env.example) is the file-based configuration template included in the submission archive. The real `.env` remains local and ignored. Copy the template only if you do not already have `.env`:

```text
# Bash
if [ ! -e .env ]; then cp .env.example .env; fi

# PowerShell
if (!(Test-Path .env)) { Copy-Item .env.example .env }
```

For a new file, generate a random local secret with `uv run --locked python -c 'import secrets; print(secrets.token_hex(32))'`, then replace the `JWT_SECRET` placeholder in `.env` with that value. Keep the value private; do not include the generation output in shared logs. Use plain `KEY=value` lines without surrounding quotes. Retain an existing secret on subsequent starts. A missing or empty `JWT_SECRET` now raises a clear startup error; there is no hard-coded fallback.

### Run the container

These commands are identical in Bash and PowerShell:

```text
# Bash or PowerShell — from the repository root.
docker build -t simple-flask-project .
docker run --rm --name simple-flask-container --env-file .env -p 127.0.0.1:8080:8080 simple-flask-project
```

Leave the server running and use a second terminal for requests. The container reads the actual `.env` at startup; its secret is not copied into the image. `docker stop simple-flask-container` stops this example and `--rm` removes it. If a container with that name already exists, inspect/reuse or stop/remove it before creating another.

### Run directly on the host

The app does not read `.env` automatically. Load the two settings before starting it:

```text
# Bash
set -a
source .env
set +a
uv run --locked python main.py

# PowerShell
Get-Content .env | ForEach-Object {
    if ($_ -match '^(JWT_SECRET|LOG_LEVEL)=(.*)$') {
        [Environment]::SetEnvironmentVariable($Matches[1], $Matches[2], 'Process')
    }
}
uv run --locked python main.py
```

Logging defaults to `INFO`; `DEBUG` includes the startup debug message. Restart the app after changing environment settings. Restarting with the same secret preserves unexpired JWTs; changing it invalidates tokens signed with the previous value.

In another terminal:

```text
# Bash
curl --fail-with-body --silent --show-error http://127.0.0.1:8080/

# PowerShell
Invoke-RestMethod -Uri 'http://127.0.0.1:8080/'
```

It returns `"Healthy"`. Use `Ctrl+C` in the server terminal to stop it.

## Dependencies and tests

`pyproject.toml` requires Python 3.13 and `uv.lock` pins the dependencies. Docker uses `python:3.13-slim`, copies uv 0.13.7, and runs `uv sync --locked --no-dev --no-cache`. The runtime image contains the locked application dependencies; Gunicorn still runs as `["gunicorn", "-b", ":8080", "main:APP"]` on port 8080.

uv manages all Python dependencies; there are no requirements exports or pip installation steps. `uv sync --locked` includes the pytest development group. CodeBuild runs all 14 tests on its host and again in a disposable container using the actual application image before publication. Only that disposable test container installs the development group; the published image retains runtime dependencies only.

```bash
uv run --locked pytest
# After an intentional change to pyproject.toml:
uv lock
uv sync --locked
```

Commit `pyproject.toml` and `uv.lock` together after dependency changes. PyJWT 2 returns a string from `jwt.encode()`; do not append `.decode('utf-8')`. `jwt.decode()` remains the token-verification API.

The course submission passed before this runtime restoration. [SUBMISSION.md](./SUBMISSION.md) and the `resubmission-*` evidence preserve the accepted legacy snapshot. The current Python 3.13/uv verification is recorded separately in [runtime test output](./evidence/python313-uv-runtime-tests.txt), [local checks](./evidence/python313-uv-local-checks.json), [cloud deployment evidence](./evidence/python313-uv-2026-11-12.json), and the companion guide's project activity log.

On **2026-11-12 at 15:18 Europe/Budapest**, application commit `8794a65d681eeeedd59f3f149034e77facc64554` passed pipeline `c5d9124c-e808-4a92-993a-471784faacb5`. CodeBuild passed 14 host tests and 14 image tests; EKS had three updated/ready/available replicas. The running image reported Python 3.13.18 and uv 0.13.7. Public health/auth/contents checks passed; missing and invalid tokens returned 401. Subsequent evidence/documentation commits contain the same application and deployment configuration.

## Project files

```text
.
├── Dockerfile                  # Python 3.13 slim, locked uv dependencies, Gunicorn
├── .env.example                # Safe file-based local configuration template
├── README.md
├── .python-version
├── aws-auth-patch.yml           # Sample Kubernetes access mapping to adapt
├── buildspec.yml               # CodeBuild phases
├── ci-cd-codepipeline.cfn.yml   # Pipeline infrastructure parameters to complete
├── iam-role-policy.json        # IAM permissions
├── main.py
├── pyproject.toml
├── uv.lock
├── simple_jwt_api.yml
├── test_main.py                 # Regression tests; extend for the project
└── trust.json                  # IAM trust policy to adapt
```

## Project steps

1. Review the Dockerfile for the Flask API and its Gunicorn entry point.
2. Build and test the container locally, supplying `JWT_SECRET` as a runtime environment variable.
3. Create an EKS cluster, manually create the IAM role CodeBuild will assume, and configure its Kubernetes access using the exercise's `aws-auth` mapping.
4. Store the secret using AWS Systems Manager Parameter Store, as described in the project instructions.
5. Create a CodePipeline pipeline triggered by GitHub commits using the supplied CloudFormation template and a GitHub access token.
6. Configure CodeBuild to build, test, and deploy the code. The buildspec retains the course's phase and command order, synchronizes dependencies with uv, and uses AWS CLI v2 for ECR login. Set its `KUBECTL_VERSION` variable to a patch release compatible with your cluster's Kubernetes minor version; the example pin is `v1.37.2` for the project's Kubernetes 1.37 cluster.

For the incremental exercises and submission requirements, follow the course project lesson.
