# CI/CD Showcase — Enterprise Pipeline

![CI Pipeline](https://github.com/YOUR_USERNAME/cicd-showcase/actions/workflows/ci.yml/badge.svg)
![CD Pipeline](https://github.com/YOUR_USERNAME/cicd-showcase/actions/workflows/cd.yml/badge.svg)
![Security Scan](https://github.com/YOUR_USERNAME/cicd-showcase/actions/workflows/nightly-security.yml/badge.svg)
[![Quality Gate](https://sonarcloud.io/api/project_badges/measure?project=YOUR_PROJECT_KEY&metric=alert_status)](https://sonarcloud.io/dashboard?id=YOUR_PROJECT_KEY)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=YOUR_PROJECT_KEY&metric=coverage)](https://sonarcloud.io/dashboard?id=YOUR_PROJECT_KEY)

A production-grade CI/CD showcase demonstrating enterprise DevOps practices:
**GitHub Actions** · **SonarCloud** · **Docker Hub** · **Terraform** · **Ansible** · **Prometheus**

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    GitHub Actions Pipeline                    │
│                                                               │
│  Push/PR → Lint → ┌─ Frontend Build+Test ─┐                 │
│                   └─ C++ Build+Test ───────┘                 │
│                           ↓                                   │
│                    SonarCloud Gate (blocking)                 │
│                           ↓                                   │
│              ┌─ Docker Frontend Push ─┐                      │
│              └─ Docker Backend Push ──┘                      │
│                           ↓                                   │
│                    Terraform Plan/Apply                       │
│                           ↓                                   │
│                    Deploy → Health Check                      │
└─────────────────────────────────────────────────────────────┘
```

## Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, nginx |
| Backend | C++17, CMake |
| CI/CD | GitHub Actions (5 workflows) |
| Quality Gate | SonarCloud |
| Containers | Docker, Docker Hub |
| IaC | Terraform (AWS S3 + CloudFront) |
| Config Mgmt | Ansible |
| Monitoring | Prometheus, Grafana, Alert Rules |
| Security | Trivy, Gitleaks, npm audit |
| Git Hooks | Pre-commit secret/lint scanner |

---

## Pipeline Workflows

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `ci.yml` | push / PR | Full build, test, scan, docker, terraform |
| `cd.yml` | CI success on main | Deploy staging → approval → production |
| `pr-validation.yml` | PR open/update | Title lint, secret scan, auto-label |
| `reusable-docker.yml` | Called by CI | Reusable Docker build/push |
| `nightly-security.yml` | Cron 2AM UTC | Trivy image scan + GitHub Security upload |

---

## Quick Start

### 1. Clone and set up

```bash
git clone https://github.com/YOUR_USERNAME/cicd-showcase.git
cd cicd-showcase
```

### 2. Run locally with Docker Compose

```bash
docker compose up --build
# Frontend → http://localhost:3000
# Backend  → http://localhost:8080
```

### 3. Run tests locally

```bash
# Frontend
cd frontend && npm ci && npm test

# C++ backend
cd backend
cmake -B build && cmake --build build
cd build && ctest --output-on-failure
```

### 4. Install pre-commit hook

```bash
cp scripts/pre-commit.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

---

## GitHub Secrets Required

Go to **Settings → Secrets and variables → Actions** and add:

| Secret | Description |
|--------|-------------|
| `DOCKERHUB_USERNAME` | Your Docker Hub username |
| `DOCKERHUB_TOKEN` | Docker Hub access token (not password) |
| `SONAR_TOKEN` | SonarCloud project token |
| `SONAR_PROJECT_KEY` | SonarCloud project key |
| `SONAR_ORGANIZATION` | SonarCloud organization slug |
| `AWS_ACCESS_KEY_ID` | AWS credentials for Terraform |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key |
| `SSH_PRIVATE_KEY` | SSH key for Ansible deployment |

---

## SonarCloud Setup

1. Go to [sonarcloud.io](https://sonarcloud.io) → sign in with GitHub
2. Create a new project → select this repo
3. Copy the **Project Key** and **Organization** into `sonar-project.properties`
4. Add `SONAR_TOKEN` to GitHub Secrets
5. The quality gate runs automatically on every push

---

## Key Design Decisions

**Parallelisation** — Frontend build+test and C++ build+test run concurrently. Docker frontend and backend build concurrently after the quality gate. This cuts total pipeline duration significantly.

**Caching strategy** — Three layers: npm dependency cache (keyed by `package-lock.json` hash), CMake build cache (keyed by source file hashes), Docker layer cache (stored in registry as `buildcache` tag).

**Blocking quality gate** — SonarCloud runs with `qualitygate.wait=true`. The Docker and Terraform jobs cannot proceed until the quality gate passes. This is the enforcement mechanism.

**Single points of failure** — SonarCloud failure is the only pipeline-blocking external dependency. Docker Hub and Terraform use `continue-on-error: true` for showcase purposes; in production these would be strict.

**Rollback strategy** — CD pipeline health checks after every deployment. On failure, the previous stable image tag is redeployed. Image tags are immutable (SHA-based), so rollback is deterministic.

---

## Monitoring & SLOs

| SLO | Target | Alert Threshold |
|-----|--------|-----------------|
| Availability | 99.5% | Error rate > 0.5% for 5 min |
| Latency (p99) | < 500ms | p99 > 500ms for 5 min |
| Error budget burn | — | 14.4x burn rate for 2 min |

---

## Python CLI Tools

```bash
# Health check any environment
python scripts/health_check.py --env staging
python scripts/health_check.py --url http://localhost:3000

# Check pipeline status
export GITHUB_TOKEN=your_token
python scripts/pipeline_status.py --repo YOUR_USERNAME/cicd-showcase
```

---

## Project Structure

```
cicd-showcase/
├── .github/
│   ├── workflows/
│   │   ├── ci.yml                  # Main CI pipeline
│   │   ├── cd.yml                  # CD deploy pipeline
│   │   ├── pr-validation.yml       # PR checks
│   │   ├── reusable-docker.yml     # Reusable Docker workflow
│   │   └── nightly-security.yml    # Scheduled security scans
│   └── labeler.yml                 # Auto PR labeling
├── frontend/                       # React 18 app
│   ├── src/
│   ├── Dockerfile                  # Multi-stage build
│   └── nginx.conf                  # SPA routing + security headers
├── backend/                        # C++17 health service
│   ├── main.cpp
│   ├── tests.cpp
│   └── CMakeLists.txt
├── docker/
│   └── Dockerfile.backend          # C++ multi-stage build
├── infra/
│   ├── terraform/                  # AWS S3 + CloudFront IaC
│   └── ansible/                    # Server configuration
├── monitoring/
│   ├── prometheus.yml              # Scrape config
│   └── alert_rules.yml             # SLO-based alerts
├── scripts/
│   ├── health_check.py             # Health check CLI
│   ├── pipeline_status.py          # Pipeline status CLI
│   └── pre-commit.sh               # Git pre-commit hook
├── sonar-project.properties        # SonarCloud config
└── docker-compose.yml              # Local development
```
