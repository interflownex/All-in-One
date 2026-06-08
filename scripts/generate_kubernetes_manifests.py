import os

MODULES = [
    "ai-core", "api-hub", "bi", "bpm", "business", "crm", "delivery", 
    "document", "erp", "finance", "health", "hr", "identity", "jobs", 
    "legal", "marketplace", "mobility", "permissions", "property", 
    "riders", "services", "stock", "tms", "vision", "wms"
]

WORKERS = {
    "outbox-dispatcher": {"type": "deployment", "replicas": 2},
    "retention-worker": {"type": "cronjob", "schedule": "0 * * * *"}
}

PROJECT_ID = "all-in-one-498012"
REPO = f"us-central1-docker.pkg.dev/{PROJECT_ID}/all-in-one-repo"
NAMESPACE = "all-in-one"

BASE_DIR = "infra/kubernetes/base"

def generate_deployment(name, image, replicas=2, port=8000):
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
          ports: [{{containerPort: {port}}}]
          readinessProbe: {{httpGet: {{path: /health, port: {port}}}}}
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

def generate_cronjob(name, image, schedule):
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
              command: ["python", "-m", "workers.{name.replace('-', '_')}.main"]
              args: ["--postgres", "--job", "retention_review_daily", "--dry-run"]
              envFrom:
                - configMapRef: {{name: platform-config}}
                - secretRef: {{name: platform-secrets-placeholder}}
"""

def main():
    if not os.path.exists(BASE_DIR):
        os.makedirs(BASE_DIR)

    # Generate Modules
    for module in MODULES:
        content = generate_deployment(module, f"{REPO}/{module}")
        with open(f"{BASE_DIR}/{module}.yaml", "w") as f:
            f.write(content)
        print(f"Generated {module}.yaml")

    # Generate Workers
    for worker, cfg in WORKERS.items():
        if cfg["type"] == "deployment":
            content = generate_deployment(worker, f"{REPO}/{worker}", replicas=cfg["replicas"])
        else:
            content = generate_cronjob(worker, f"{REPO}/{worker}", cfg["schedule"])
        
        with open(f"{BASE_DIR}/{worker}.yaml", "w") as f:
            f.write(content)
        print(f"Generated {worker}.yaml")

    # Update kustomization.yaml if it exists, or create it
    resources = [f"{m}.yaml" for m in MODULES] + [f"{w}.yaml" for w in WORKERS.keys()] + ["platform.yaml", "retention-alerting.yaml"]
    
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
