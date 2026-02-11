# OpenShift 4.19 - Quick Reference for NotebookLM MCP

Fast command reference for OpenShift deployment and management.

## Login & Project

```bash
# Login
oc login --token=<token> --server=https://api.cluster.com:6443

# Create project
oc new-project notebooklm-mcp

# Switch project
oc project notebooklm-mcp

# Check current project
oc project
```

## Deploy with Helm

```bash
# Install
helm install notebooklm-mcp ./helm/notebooklm-mcp-openshift -n notebooklm-mcp

# Install with custom values
helm install notebooklm-mcp ./helm/notebooklm-mcp-openshift \
  -f values-prod.yaml -n notebooklm-mcp

# Upgrade
helm upgrade notebooklm-mcp ./helm/notebooklm-mcp-openshift -n notebooklm-mcp

# Uninstall
helm uninstall notebooklm-mcp -n notebooklm-mcp

# Status
helm status notebooklm-mcp -n notebooklm-mcp

# History
helm history notebooklm-mcp -n notebooklm-mcp

# Rollback
helm rollback notebooklm-mcp 1 -n notebooklm-mcp
```

## Manage Pods

```bash
# List pods
oc get pods -n notebooklm-mcp

# Describe pod
oc describe pod <pod-name> -n notebooklm-mcp

# Logs
oc logs -f <pod-name> -n notebooklm-mcp
oc logs -f deployment/notebooklm-mcp -n notebooklm-mcp

# Shell into pod
oc rsh <pod-name>
oc rsh deployment/notebooklm-mcp

# Execute command
oc exec <pod-name> -- command

# Delete pod (recreates automatically)
oc delete pod <pod-name> -n notebooklm-mcp
```

## Deployments

```bash
# List deployments
oc get deployments -n notebooklm-mcp

# Describe deployment
oc describe deployment notebooklm-mcp -n notebooklm-mcp

# Scale
oc scale deployment notebooklm-mcp --replicas=3 -n notebooklm-mcp

# Rollout restart
oc rollout restart deployment/notebooklm-mcp -n notebooklm-mcp

# Rollout status
oc rollout status deployment/notebooklm-mcp -n notebooklm-mcp

# Rollout history
oc rollout history deployment/notebooklm-mcp -n notebooklm-mcp

# Undo rollout
oc rollout undo deployment/notebooklm-mcp -n notebooklm-mcp

# Update image
oc set image deployment/notebooklm-mcp \
  notebooklm-mcp-openshift=new-image:tag -n notebooklm-mcp

# Update env
oc set env deployment/notebooklm-mcp LOG_LEVEL=DEBUG -n notebooklm-mcp
```

## Routes

```bash
# List routes
oc get routes -n notebooklm-mcp

# Get route URL
oc get route notebooklm-mcp -o jsonpath='{.spec.host}'

# Describe route
oc describe route notebooklm-mcp -n notebooklm-mcp

# Edit route
oc edit route notebooklm-mcp -n notebooklm-mcp

# Delete route
oc delete route notebooklm-mcp -n notebooklm-mcp

# Create route
oc expose service notebooklm-mcp --hostname=notebooklm.apps.cluster.com -n notebooklm-mcp

# Test route
curl https://$(oc get route notebooklm-mcp -o jsonpath='{.spec.host}')
```

## Services

```bash
# List services
oc get svc -n notebooklm-mcp

# Describe service
oc describe svc notebooklm-mcp -n notebooklm-mcp

# Port forward
oc port-forward svc/notebooklm-mcp 8080:8080 -n notebooklm-mcp
```

## Storage

```bash
# List PVCs
oc get pvc -n notebooklm-mcp

# Describe PVC
oc describe pvc notebooklm-mcp -n notebooklm-mcp

# List storage classes
oc get storageclass

# Check PV
oc get pv

# PVC usage
oc get pvc notebooklm-mcp -o jsonpath='{.status.capacity.storage}' -n notebooklm-mcp
```

## Security

```bash
# List SCCs
oc get scc

# Describe SCC
oc describe scc restricted-v2

# Add SCC to service account
oc adm policy add-scc-to-user restricted-v2 -z notebooklm-mcp -n notebooklm-mcp

# Check which SCC pod is using
oc get pod <pod-name> -o yaml | grep openshift.io/scc

# List service accounts
oc get sa -n notebooklm-mcp

# Get service account token
oc sa get-token notebooklm-mcp -n notebooklm-mcp
```

## ConfigMaps & Secrets

```bash
# List ConfigMaps
oc get configmap -n notebooklm-mcp

# View ConfigMap
oc get configmap notebooklm-mcp -o yaml -n notebooklm-mcp

# Edit ConfigMap
oc edit configmap notebooklm-mcp -n notebooklm-mcp

# List secrets
oc get secrets -n notebooklm-mcp

# View secret (decoded)
oc extract secret/notebooklm-mcp --to=- -n notebooklm-mcp

# Create secret
oc create secret generic my-secret --from-literal=key=value -n notebooklm-mcp
```

## NetworkPolicy

```bash
# List network policies
oc get networkpolicy -n notebooklm-mcp

# Describe network policy
oc describe networkpolicy notebooklm-mcp -n notebooklm-mcp

# Test connectivity
oc run test --rm -it --image=curlimages/curl -- curl http://notebooklm-mcp:8080
```

## ImageStreams & BuildConfigs

```bash
# List ImageStreams
oc get imagestream -n notebooklm-mcp

# Describe ImageStream
oc describe imagestream notebooklm-mcp -n notebooklm-mcp

# Trigger import
oc import-image notebooklm-mcp:latest -n notebooklm-mcp

# List BuildConfigs
oc get bc -n notebooklm-mcp

# Start build
oc start-build notebooklm-mcp -n notebooklm-mcp

# Follow build logs
oc logs -f bc/notebooklm-mcp -n notebooklm-mcp

# List builds
oc get builds -n notebooklm-mcp

# Cancel build
oc cancel-build <build-name> -n notebooklm-mcp
```

## Monitoring

```bash
# Get metrics
oc adm top pod -n notebooklm-mcp
oc adm top node

# List ServiceMonitors
oc get servicemonitor -n notebooklm-mcp

# List PrometheusRules
oc get prometheusrule -n notebooklm-mcp

# View alerts (requires cluster-monitoring access)
oc get prometheusrule -n openshift-monitoring
```

## Events & Logs

```bash
# Get events
oc get events -n notebooklm-mcp --sort-by='.lastTimestamp'

# Watch events
oc get events -n notebooklm-mcp -w

# Pod logs
oc logs <pod-name> -n notebooklm-mcp

# Previous pod logs (if crashed)
oc logs <pod-name> --previous -n notebooklm-mcp

# All container logs
oc logs <pod-name> --all-containers -n notebooklm-mcp

# Stream logs
oc logs -f deployment/notebooklm-mcp -n notebooklm-mcp
```

## Debugging

```bash
# Debug pod
oc debug pod/<pod-name> -n notebooklm-mcp

# Debug deployment
oc debug deployment/notebooklm-mcp -n notebooklm-mcp

# Run temporary pod
oc run debug --rm -it --image=registry.access.redhat.com/ubi9/ubi -- bash

# Check pod status
oc get pod <pod-name> -o wide -n notebooklm-mcp

# Describe all resources
oc describe all -l app.kubernetes.io/name=notebooklm-mcp-openshift -n notebooklm-mcp
```

## Resource Management

```bash
# Get all resources
oc get all -n notebooklm-mcp

# Get all with labels
oc get all -l app.kubernetes.io/name=notebooklm-mcp-openshift -n notebooklm-mcp

# Describe all
oc describe all -l app.kubernetes.io/name=notebooklm-mcp-openshift -n notebooklm-mcp

# Delete all (careful!)
oc delete all -l app.kubernetes.io/name=notebooklm-mcp-openshift -n notebooklm-mcp

# Export resources
oc get all -o yaml > backup.yaml
```

## Quotas & LimitRanges

```bash
# Check quota
oc get quota -n notebooklm-mcp

# Describe quota
oc describe quota -n notebooklm-mcp

# Check limit ranges
oc get limitrange -n notebooklm-mcp
```

## Authentication

```bash
# Get pod
POD=$(oc get pod -l app.kubernetes.io/name=notebooklm-mcp-openshift -o jsonpath='{.items[0].metadata.name}')

# Shell into pod
oc rsh $POD

# Run auth script
uv run python scripts/setup_auth.py

# Check auth data
ls -la /app/chrome-user-data
```

## Backup & Restore (OADP)

```bash
# Create backup
oc create -f - <<EOF
apiVersion: velero.io/v1
kind: Backup
metadata:
  name: notebooklm-backup
  namespace: openshift-adp
spec:
  includedNamespaces:
  - notebooklm-mcp
EOF

# List backups
oc get backups -n openshift-adp

# Restore
oc create -f - <<EOF
apiVersion: velero.io/v1
kind: Restore
metadata:
  name: notebooklm-restore
  namespace: openshift-adp
spec:
  backupName: notebooklm-backup
EOF
```

## Troubleshooting Commands

```bash
# Full diagnostic
oc get all,pvc,secret,configmap,route -n notebooklm-mcp

# Check pod details
oc get pod <pod-name> -o yaml -n notebooklm-mcp

# Check pod conditions
oc get pod <pod-name> -o jsonpath='{.status.conditions}' -n notebooklm-mcp | jq

# Resource usage
oc adm top pod <pod-name> -n notebooklm-mcp

# Cluster info
oc cluster-info

# API versions
oc api-resources

# Check permissions
oc auth can-i create pods --namespace notebooklm-mcp
oc auth can-i create scc --as system:serviceaccount:notebooklm-mcp:notebooklm-mcp
```

## Export & Template

```bash
# Export deployment
oc get deployment notebooklm-mcp -o yaml > deployment.yaml

# Create template
oc export deployment,svc,route notebooklm-mcp --as-template=notebooklm > template.yaml

# Process template
oc process -f template.yaml -p PARAM=value | oc apply -f -
```

## Cleanup

```bash
# Delete project (deletes everything)
oc delete project notebooklm-mcp

# Delete specific resources
helm uninstall notebooklm-mcp -n notebooklm-mcp
oc delete all -l app.kubernetes.io/name=notebooklm-mcp-openshift -n notebooklm-mcp
oc delete pvc notebooklm-mcp -n notebooklm-mcp
```

## Useful Aliases

```bash
# Add to ~/.bashrc or ~/.zshrc
alias ocg='oc get'
alias ocd='oc describe'
alias ocl='oc logs -f'
alias oce='oc exec -it'
alias ocr='oc rsh'
alias ocgp='oc get pods'
alias ocgd='oc get deployments'
alias ocgs='oc get svc'
alias ocgr='oc get routes'
```

## Common Patterns

```bash
# Get pod name and exec
POD=$(oc get pod -l app=notebooklm-mcp -o jsonpath='{.items[0].metadata.name}')
oc exec -it $POD -- /bin/bash

# Follow logs of latest pod
oc logs -f $(oc get pod -l app=notebooklm-mcp -o jsonpath='{.items[0].metadata.name}')

# Port forward to latest pod
oc port-forward $(oc get pod -l app=notebooklm-mcp -o jsonpath='{.items[0].metadata.name}') 8080:8080

# Restart all pods
oc delete pods -l app.kubernetes.io/name=notebooklm-mcp-openshift
```

---

Save this file for quick reference! 🔖
