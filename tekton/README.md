# Tekton CD Pipeline

This directory contains the Tekton pipeline definitions for the Customer Accounts Microservice.

## Pipeline DAG

```
clone ──┬── lint ────┐
        └── tests ───┴── build ── deploy
```

| Task | Runs After | Description |
|------|-----------|-------------|
| `clone` | — | Clones the Git repo using `git-clone` from Tekton Catalog |
| `lint` | clone | Runs `flake8` linter (from Tekton Catalog) |
| `tests` | clone | Runs `nose2` unit tests (custom task) |
| `build` | lint + tests | Builds & pushes Docker image using `kaniko` |
| `deploy` | build | Deploys to Kubernetes using `kubectl apply` |

## Files

| File | Purpose |
|------|---------|
| `pvc.yaml` | PersistentVolumeClaim for the shared pipeline workspace |
| `tasks.yaml` | Custom tasks: `nose` (tests) and `deploy-kubectl` (deploy) |
| `pipeline.yaml` | The full `cd-pipeline` Pipeline definition |

## Prerequisites

Install catalog tasks into your cluster:

```bash
# git-clone
kubectl apply -f https://raw.githubusercontent.com/tektoncd/catalog/main/task/git-clone/0.9/git-clone.yaml

# flake8
kubectl apply -f https://raw.githubusercontent.com/tektoncd/catalog/main/task/flake8/0.1/flake8.yaml

# kaniko (build & push)
kubectl apply -f https://raw.githubusercontent.com/tektoncd/catalog/main/task/kaniko/0.6/kaniko.yaml
```

## Setup

```bash
# 1. Create workspace PVC
kubectl create -f tekton/pvc.yaml

# 2. Install custom tasks
kubectl apply -f tekton/tasks.yaml

# 3. Apply the pipeline
kubectl apply -f tekton/pipeline.yaml
```

## Run the Pipeline

```bash
export GITHUB_ACCOUNT=<your-github-username>
export DOCKERHUB_USER=<your-dockerhub-username>

tkn pipeline start cd-pipeline \
    -p repo-url="https://github.com/$GITHUB_ACCOUNT/devops-capstone-project.git" \
    -p branch="main" \
    -p build-image="docker.io/$DOCKERHUB_USER/accounts:latest" \
    -w name=pipeline-workspace,claimName=pipelinerun-pvc \
    --showlog

# Check run status
tkn pipelinerun ls
```

## Adapations vs IBM Lab (OpenShift → Local Kubernetes)

| Lab (OpenShift) | This Repo (Local k8s) |
|---|---|
| `openshift-client` ClusterTask | `deploy-kubectl` custom task using `bitnami/kubectl` |
| `buildah` ClusterTask | `kaniko` catalog task |
| OpenShift internal registry | Docker Hub |
| `oc apply` | `kubectl apply` |
