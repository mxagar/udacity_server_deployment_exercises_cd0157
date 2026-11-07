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
- Python 3.13 and [uv](https://docs.astral.sh/uv/getting-started/installation/) 0.13.7 or newer. Python can be installed by uv or downloaded from [python.org](https://www.python.org/downloads/).
- A terminal: the default terminal on macOS/Linux; Git Bash or Windows Subsystem for Linux (WSL) on Windows. Gunicorn runs on Windows through WSL or a Linux container.
- For cloud deployment: an AWS account, [AWS CLI v2](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html), [eksctl](https://docs.aws.amazon.com/eks/latest/eksctl/installation.html), and [kubectl](https://kubernetes.io/docs/tasks/tools/). Configure the appropriate AWS profile and keep exercise resources in a single supported region, such as `eu-central-1`.

## Initial setup and local run

The original [Udacity starter repository](https://github.com/udacity/cd0157-Server-Deployment-and-Containerization) has been forked here. For a standalone checkout:

```bash
git clone https://github.com/mxagar/udacity_server_deployment_exercises_cd0157.git
cd udacity_server_deployment_exercises_cd0157
uv python install 3.13
uv sync --locked
export JWT_SECRET="$(uv run --locked python -c 'import secrets; print(secrets.token_hex(32))')"
export LOG_LEVEL=DEBUG
uv run --locked python main.py
```

If this repository is already checked out as a submodule, enter that directory and start at `uv python install`. uv creates its own `.venv`; activation is unnecessary. Keep the secret stable for the lifetime of the issued tokens. Logging defaults to `INFO`; `DEBUG` includes the startup debug message. Restart the app after changing its environment settings.

In another terminal:

```bash
curl --fail-with-body --silent --show-error http://127.0.0.1:8080/
```

It returns `"Healthy"`. Use `Ctrl+C` in the server terminal to stop it.

## Dependencies and tests

`pyproject.toml` declares the runtime dependencies (Flask, PyJWT, and Gunicorn) and the development test dependency (pytest). `uv.lock` records exact versions; `.python-version` selects Python 3.13. Docker and CodeBuild use the same project and lockfile.

```bash
uv run --locked pytest
# After an intentional change to pyproject.toml:
uv lock
uv sync --locked
```

Commit `pyproject.toml` and `uv.lock` together after dependency changes. PyJWT 2 returns a string from `jwt.encode()`; do not append `.decode('utf-8')`. `jwt.decode()` remains the token-verification API.

## Project files

```text
.
├── Dockerfile                  # Python 3.13, uv, and Gunicorn
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
6. Configure CodeBuild to build, test, and deploy the code. The buildspec retains the course's phase and command order, synchronizes dependencies with uv, and uses AWS CLI v2 for ECR login. Set its `KUBECTL_VERSION` variable to a patch release compatible with your cluster's Kubernetes minor version; the example pin is `v1.34.13`.

For the incremental exercises and submission requirements, follow the course project lesson.
