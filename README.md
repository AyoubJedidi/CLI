# cicd-cli-tool

Auto-detect your project framework and generate CI/CD pipeline files instantly.

## Installation

```bash
pip install cicd-cli-tool
```

## Supported Frameworks

Python, Node.js, Java, Maven, Gradle, .NET

## Commands

### `cicd init`
Detect your project and generate pipeline files.

```bash
# Generate Jenkins pipeline (default)
cicd init

# Generate GitLab CI
cicd init --platforms gitlab

# Generate for multiple platforms
cicd init --platforms jenkins,gitlab,github

# Force a specific framework
cicd init --framework python --platforms github

# Deploy to a cloud provider
cicd init --cloud-provider aws --deployment-type webapp
cicd init --cloud-provider azure --deployment-type instance
```

**Options:**

| Flag | Short | Description | Default |
|------|-------|-------------|---------|
| `--platforms` | `-p` | `jenkins`, `gitlab`, `github` (comma-separated) | `jenkins` |
| `--framework` | `-f` | `python`, `node`, `java`, `maven`, `gradle`, `dotnet` | auto-detect |
| `--cloud-provider` | `-cp` | `local`, `aws`, `azure`, `gcp` | `local` |
| `--deployment-type` | `-dt` | `webapp`, `instance` | `webapp` |

---

### `cicd detect`
Detect project info without generating any files.

```bash
cicd detect
cicd detect /path/to/project
```

---

### `cicd list`
List all supported frameworks and platforms.

```bash
cicd list
```

---

### `cicd options`
Show all available deployment options and their values.

```bash
cicd options
```

## Examples

```bash
# Python project → GitHub Actions + deploy to GCP
cicd init --framework python --platforms github --cloud-provider gcp

# Node.js project → Jenkins + GitLab CI
cicd init --platforms jenkins,gitlab

# Java project → all platforms + AWS webapp
cicd init --framework java --platforms jenkins,gitlab,github --cloud-provider aws
```
