# Kubernetes CronJob Wiring

## Purpose
- This document is the `Checkpoint 8H` runbook for wiring stale-backup checks on Kubernetes.
- It provides one concrete CronJob manifest path for orchestrated deployments.

## Manifest
- `infra/k8s/backup-stale-alert-cronjob.example.yaml`

## Apply resources
```bash
kubectl apply -f infra/k8s/backup-stale-alert-cronjob.example.yaml
```

## Validate behavior
1. Confirm CronJob exists:
```bash
kubectl get cronjob myatelier-backup-stale-alert-check
```
2. Trigger one manual run:
```bash
kubectl create job --from=cronjob/myatelier-backup-stale-alert-check myatelier-backup-stale-alert-check-manual
```
3. Review logs:
```bash
kubectl logs job/myatelier-backup-stale-alert-check-manual
```
4. Confirm backend audit log includes `ops.backup_stale_check_run`.

## Update schedule
- Edit `spec.schedule` in the manifest (current default: hourly `0 * * * *`).

## Remove resources
```bash
kubectl delete -f infra/k8s/backup-stale-alert-cronjob.example.yaml
```

## Security note
- Replace default placeholder credentials in Secret before deployment.
- Restrict namespace/service-account permissions as needed by cluster policy.
- Keep endpoint credentials in managed secret systems where possible.
