import json
import os
from pathlib import Path

MODULES = [
    "ai-core", "api-hub", "bi", "bpm", "business", "crm", "delivery",
    "document", "erp", "finance", "health", "hr", "identity", "jobs",
    "legal", "marketplace", "mobility", "permissions", "property",
    "riders", "services", "stock", "tms", "vision", "wms"
]

WORKERS = {
    "outbox-dispatcher": {
        "type": "deployment",
        "replicas": 2,
        "readiness_mode": "exec",
        "readiness_timeout_seconds": 5,
        "image_pull_policy": "Always",
    },
    "retention-worker": {
        "type": "cronjob",
        "schedule": "0 * * * *",
        "image_pull_policy": "Always",
    },
}

PROJECT_ID = "all-in-one-498012"
REPO = f"us-central1-docker.pkg.dev/{PROJECT_ID}/all-in-one-repo"
NAMESPACE = "all-in-one"

BASE_DIR = "infra/kubernetes/base"
OUTBOX_DASHBOARD_SOURCE = Path("config/observability/outbox_dashboard.json")
COMMERCIAL_DASHBOARD_SOURCE = Path("config/observability/commercial_dashboard.json")

def generate_deployment(
    name,
    image,
    replicas=2,
    port=8000,
    readiness_mode="http",
    readiness_timeout_seconds=None,
    image_pull_policy="IfNotPresent",
):
    if readiness_mode == "exec":
        readiness_probe = """\
          readinessProbe:
            exec:
              command:
                - python
                - -m
                - workers.outbox_dispatcher.main
                - --metrics"""
    else:
        readiness_probe = f"""\
          readinessProbe:
            httpGet:
              path: /health
              port: {port}"""
    if readiness_timeout_seconds is not None:
        readiness_probe += f"\n            timeoutSeconds: {readiness_timeout_seconds}"
    return f"""---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {name}
  namespace: {NAMESPACE}
spec:
  replicas: {replicas}
  selector:
    matchLabels: {{app: {name}}}
  template:
    metadata:
      labels: {{app: {name}}}
    spec:
      containers:
        - name: {name}
          image: {image}:latest
          imagePullPolicy: {image_pull_policy}
          ports: [{{containerPort: {port}}}]
{readiness_probe}
          envFrom:
            - configMapRef: {{name: platform-config}}
            - secretRef: {{name: platform-secrets-placeholder}}
---
apiVersion: v1
kind: Service
metadata:
  name: {name}
  namespace: {NAMESPACE}
spec:
  selector: {{app: {name}}}
  ports: [{{port: 80, targetPort: {port}}}]
"""

def generate_cronjob(name, image, schedule, image_pull_policy="IfNotPresent"):
    return f"""---
apiVersion: batch/v1
kind: CronJob
metadata:
  name: {name}
  namespace: {NAMESPACE}
spec:
  schedule: "{schedule}"
  concurrencyPolicy: Forbid
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 3
  jobTemplate:
    spec:
      backoffLimit: 2
      template:
        metadata:
          labels: {{app: {name}}}
        spec:
          restartPolicy: OnFailure
          containers:
            - name: {name}
              image: {image}:latest
              imagePullPolicy: {image_pull_policy}
              command: ["python", "-m", "workers.{name.replace('-', '_')}.main"]
              args: ["--postgres", "--job", "retention_review_daily", "--dry-run"]
              envFrom:
                - configMapRef: {{name: platform-config}}
                - secretRef: {{name: platform-secrets-placeholder}}
"""


def generate_dashboard_configmap(name: str, dashboard_source: Path) -> str:
    dashboard = json.loads(dashboard_source.read_text(encoding="utf-8"))
    dashboard_json = json.dumps(dashboard, ensure_ascii=False, indent=2)
    dashboard_yaml = "\n".join(f"    {line}" for line in dashboard_json.splitlines())
    return f"""---
apiVersion: v1
kind: ConfigMap
metadata:
  name: {name}
  namespace: {NAMESPACE}
  labels:
    app: outbox-dispatcher
    domain: operations
    grafana_dashboard: "1"
data:
  {name}.json: |-
{dashboard_yaml}
"""

def main():
    if not os.path.exists(BASE_DIR):
        os.makedirs(BASE_DIR)

    # Generate Modules
    for module in MODULES:
        if module == "outbox-dispatcher":
            content = generate_deployment(
                module,
                f"{REPO}/{module}",
                readiness_mode="exec",
                readiness_timeout_seconds=5,
                image_pull_policy="Always",
            )
        else:
            content = generate_deployment(module, f"{REPO}/{module}")
        with open(f"{BASE_DIR}/{module}.yaml", "w") as f:
            f.write(content)
        print(f"Generated {module}.yaml")

    # Generate Workers
    for worker, cfg in WORKERS.items():
        if cfg["type"] == "deployment":
            content = generate_deployment(
                worker,
                f"{REPO}/{worker}",
                replicas=cfg["replicas"],
                readiness_mode=cfg.get("readiness_mode", "http"),
                readiness_timeout_seconds=cfg.get("readiness_timeout_seconds"),
                image_pull_policy=cfg.get("image_pull_policy", "IfNotPresent"),
            )
        else:
            content = generate_cronjob(
                worker,
                f"{REPO}/{worker}",
                cfg["schedule"],
                image_pull_policy=cfg.get("image_pull_policy", "IfNotPresent"),
            )

        with open(f"{BASE_DIR}/{worker}.yaml", "w") as f:
            f.write(content)
        print(f"Generated {worker}.yaml")

    with open(f"{BASE_DIR}/outbox-dashboard.yaml", "w") as f:
        f.write(generate_dashboard_configmap("outbox-dispatcher-dashboard", OUTBOX_DASHBOARD_SOURCE))
    print("Generated outbox-dashboard.yaml")

    with open(f"{BASE_DIR}/commercial-dashboard.yaml", "w") as f:
        f.write(generate_dashboard_configmap("commercial-dashboard", COMMERCIAL_DASHBOARD_SOURCE))
    print("Generated commercial-dashboard.yaml")

    # Update kustomization.yaml if it exists, or create it
    resources = [f"{m}.yaml" for m in MODULES] + [f"{w}.yaml" for w in WORKERS.keys()] + ["platform.yaml", "outbox-alerting.yaml", "outbox-dashboard.yaml", "commercial-dashboard.yaml", "retention-alerting.yaml"]

    kustomization = f"""apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
{chr(10).join([f"  - {r}" for r in resources])}
"""
    with open(f"{BASE_DIR}/kustomization.yaml", "w") as f:
        f.write(kustomization)
    print("Generated kustomization.yaml")

if __name__ == "__main__":
    main()
