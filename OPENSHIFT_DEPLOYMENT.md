# NotebookLM MCP Server - OpenShift 4.19 Deployment Guide

Complete deployment guide for Red Hat OpenShift Container Platform 4.19.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Deployment Methods](#deployment-methods)
- [Security Configuration](#security-configuration)
- [Storage Configuration](#storage-configuration)
- [Networking](#networking)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

---

## Prerequisites

### OpenShift Cluster
- OpenShift Container Platform 4.19
- Cluster admin access (for SCC creation) or namespace admin
- Storage class available (OCS, EBS, Azure Disk, etc.)

### Client Tools
```bash
# Install OpenShift CLI
# macOS
brew install openshift-cli

# Linux
wget https://mirror.openshift.com/pub/openshift-v4/clients/ocp/latest/openshift-client-linux.tar.gz
tar xzf openshift-client-linux.tar.gz
sudo mv oc /usr/local/bin/

# Verify installation
oc version
```

### Helm CLI
```bash
# Install Helm 3.x
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Verify
helm version
```

### Access Requirements
- Google account with NotebookLM access
- Network access to notebooklm.google.com

---

## Quick Start

### 1. Login to OpenShift

```bash
# Login via web console token
oc login --token=<your-token> --server=https://api.your-cluster.com:6443

# Or via username/password
oc login -u <username> -p <password> https://api.your-cluster.com:6443

# Verify login
oc whoami
oc cluster-info
```

### 2. Create Project

```bash
# Create a new project (namespace)
oc new-project notebooklm-mcp

# Or use existing project
oc project notebooklm-mcp
```

### 3. Install with Helm

```bash
# Clone repository
git clone https://github.com/yourusername/notebooklm-mcp.git
cd notebooklm-mcp

# Install Helm chart
helm install notebooklm-mcp ./helm/notebooklm-mcp-openshift \
  --namespace notebooklm-mcp

# Check deployment
oc get all -l app.kubernetes.io/name=notebooklm-mcp-openshift
```

### 4. Authenticate with Google

```bash
# Get pod name
POD=$(oc get pod -l app.kubernetes.io/name=notebooklm-mcp-openshift -o jsonpath='{.items[0].metadata.name}')

# Connect to pod
oc rsh $POD

# Run authentication
uv run python scripts/setup_auth.py

# Exit pod
exit
```

### 5. Access the Application

```bash
# Get route URL
oc get route notebooklm-mcp -o jsonpath='{.spec.host}'

# Open in browser or use curl
curl https://$(oc get route notebooklm-mcp -o jsonpath='{.spec.host}')
```

---

## Deployment Methods

### Method 1: Helm Chart (Recommended)

#### Basic Installation

```bash
helm install notebooklm-mcp ./helm/notebooklm-mcp-openshift \
  --namespace notebooklm-mcp \
  --create-namespace
```

#### Custom Values Installation

Create `values-openshift.yaml`:

```yaml
# Custom values for OpenShift deployment
image:
  repository: image-registry.openshift-image-registry.svc:5000/notebooklm-mcp/notebooklm-mcp
  tag: "latest"

resources:
  limits:
    cpu: 2000m
    memory: 3Gi
  requests:
    cpu: 1000m
    memory: 2Gi

persistence:
  enabled: true
  storageClass: "ocs-storagecluster-ceph-rbd"
  size: 2Gi

route:
  enabled: true
  host: "notebooklm.apps.your-cluster.com"
  tls:
    enabled: true
    termination: edge

monitoring:
  enabled: true
  serviceMonitor:
    enabled: true

networkPolicy:
  enabled: true
```

Install with custom values:

```bash
helm install notebooklm-mcp ./helm/notebooklm-mcp-openshift \
  -f values-openshift.yaml \
  --namespace notebooklm-mcp \
  --create-namespace
```

#### Upgrade Deployment

```bash
# Upgrade with new values
helm upgrade notebooklm-mcp ./helm/notebooklm-mcp-openshift \
  -f values-openshift.yaml \
  --namespace notebooklm-mcp

# Check upgrade status
helm status notebooklm-mcp -n notebooklm-mcp

# View history
helm history notebooklm-mcp -n notebooklm-mcp

# Rollback if needed
helm rollback notebooklm-mcp 1 -n notebooklm-mcp
```

### Method 2: OpenShift Templates

Create OpenShift template:

```bash
# Process Helm chart to OpenShift template
helm template notebooklm-mcp ./helm/notebooklm-mcp-openshift \
  --namespace notebooklm-mcp > openshift-template.yaml

# Apply template
oc apply -f openshift-template.yaml -n notebooklm-mcp
```

### Method 3: Using BuildConfig (Build from Source)

Enable BuildConfig in values:

```yaml
buildConfig:
  enabled: true
  strategy: docker
  git:
    uri: "https://github.com/yourusername/notebooklm-mcp.git"
    ref: "main"
  triggers:
    - type: ConfigChange
    - type: ImageChange

imageStream:
  enabled: true
```

Deploy and build:

```bash
helm install notebooklm-mcp ./helm/notebooklm-mcp-openshift \
  --set buildConfig.enabled=true \
  --set imageStream.enabled=true \
  --namespace notebooklm-mcp

# Watch build
oc logs -f bc/notebooklm-mcp -n notebooklm-mcp

# Check build status
oc get builds -n notebooklm-mcp
```

### Method 4: Using oc CLI (Manual)

```bash
# Create all resources individually
oc create -f helm/notebooklm-mcp-openshift/templates/serviceaccount.yaml
oc create -f helm/notebooklm-mcp-openshift/templates/persistentvolumeclaim.yaml
oc create -f helm/notebooklm-mcp-openshift/templates/configmap.yaml
oc create -f helm/notebooklm-mcp-openshift/templates/deployment.yaml
oc create -f helm/notebooklm-mcp-openshift/templates/service.yaml
oc create -f helm/notebooklm-mcp-openshift/templates/route.yaml
```

---

## Security Configuration

### SecurityContextConstraints (SCC)

OpenShift uses SCCs instead of PodSecurityPolicies.

#### Option 1: Use Restricted SCC (Recommended)

```yaml
# In values.yaml
securityContext:
  sccName: "restricted-v2"  # Default in OpenShift 4.11+
  createCustomSCC: false
```

The application is designed to run with the restricted SCC.

#### Option 2: Create Custom SCC

For specific Chromium requirements:

```yaml
# In values.yaml
securityContext:
  createCustomSCC: true
  customSCC:
    allowPrivilegeEscalation: false
    allowPrivilegedContainer: false
    requiredDropCapabilities:
      - ALL
    runAsUser:
      type: MustRunAsRange
      uidRangeMin: 1000
      uidRangeMax: 65535
```

Deploy with custom SCC:

```bash
helm install notebooklm-mcp ./helm/notebooklm-mcp-openshift \
  --set securityContext.createCustomSCC=true \
  --namespace notebooklm-mcp
```

Verify SCC:

```bash
# List SCCs
oc get scc

# View custom SCC
oc describe scc notebooklm-mcp-scc

# Check which SCC pod is using
oc get pod -l app.kubernetes.io/name=notebooklm-mcp-openshift -o yaml | grep openshift.io/scc
```

#### Grant SCC to Service Account

If using existing SCC:

```bash
# Grant anyuid SCC (if needed, not recommended)
oc adm policy add-scc-to-user anyuid -z notebooklm-mcp -n notebooklm-mcp

# Or restricted-v2 (default)
oc adm policy add-scc-to-user restricted-v2 -z notebooklm-mcp -n notebooklm-mcp

# Verify
oc get rolebinding -n notebooklm-mcp | grep scc
```

### SELinux Context

OpenShift automatically applies SELinux contexts. Verify:

```bash
oc get pod -l app.kubernetes.io/name=notebooklm-mcp-openshift -o jsonpath='{.items[0].spec.securityContext}'
```

---

## Storage Configuration

### Storage Classes

Check available storage classes:

```bash
oc get storageclass
```

Common OpenShift storage classes:

| Storage Class | Type | Use Case |
|---------------|------|----------|
| `ocs-storagecluster-ceph-rbd` | Block (RWO) | Single pod, high performance |
| `ocs-storagecluster-cephfs` | File (RWX) | Multi-pod, shared access |
| `gp3-csi` | AWS EBS | Cloud (AWS) |
| `managed-premium` | Azure Disk | Cloud (Azure) |

### Configure Storage

```yaml
# values-storage.yaml
persistence:
  enabled: true
  storageClass: "ocs-storagecluster-ceph-rbd"
  accessMode: ReadWriteOnce
  size: 2Gi
```

For multi-replica deployments:

```yaml
persistence:
  storageClass: "ocs-storagecluster-cephfs"
  accessMode: ReadWriteMany
  size: 5Gi

replicaCount: 3
```

### Manual PVC Creation

```bash
cat <<EOF | oc apply -f -
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: notebooklm-chrome-data
  namespace: notebooklm-mcp
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 2Gi
  storageClassName: ocs-storagecluster-ceph-rbd
EOF
```

Use existing PVC:

```bash
helm install notebooklm-mcp ./helm/notebooklm-mcp-openshift \
  --set persistence.existingClaim=notebooklm-chrome-data \
  --namespace notebooklm-mcp
```

### Backup with OADP

OpenShift API for Data Protection (Velero):

```bash
# Install OADP operator
oc create -f https://raw.githubusercontent.com/openshift/oadp-operator/master/config/samples/oadp_v1alpha1_dataprotectionapplication.yaml

# Create backup
oc create -f - <<EOF
apiVersion: velero.io/v1
kind: Backup
metadata:
  name: notebooklm-mcp-backup
  namespace: openshift-adp
spec:
  includedNamespaces:
  - notebooklm-mcp
  storageLocation: default
  ttl: 720h
EOF

# List backups
oc get backups -n openshift-adp

# Restore
oc create -f - <<EOF
apiVersion: velero.io/v1
kind: Restore
metadata:
  name: notebooklm-mcp-restore
  namespace: openshift-adp
spec:
  backupName: notebooklm-mcp-backup
EOF
```

---

## Networking

### Routes (OpenShift-native)

Routes are the preferred way to expose services in OpenShift.

#### HTTP Route

```yaml
route:
  enabled: true
  host: "notebooklm.apps.cluster.example.com"
  tls:
    enabled: false
```

#### HTTPS Route with Edge Termination

```yaml
route:
  enabled: true
  host: "notebooklm.apps.cluster.example.com"
  tls:
    enabled: true
    termination: edge
    insecureEdgeTerminationPolicy: Redirect
```

#### Custom Certificate

```yaml
route:
  tls:
    enabled: true
    termination: edge
    certificate: |
      -----BEGIN CERTIFICATE-----
      ...
      -----END CERTIFICATE-----
    key: |
      -----BEGIN PRIVATE KEY-----
      ...
      -----END PRIVATE KEY-----
    caCertificate: |
      -----BEGIN CERTIFICATE-----
      ...
      -----END CERTIFICATE-----
```

#### Get Route Information

```bash
# List routes
oc get routes -n notebooklm-mcp

# Get route URL
oc get route notebooklm-mcp -o jsonpath='{.spec.host}'

# Describe route
oc describe route notebooklm-mcp -n notebooklm-mcp

# Test route
curl -I https://$(oc get route notebooklm-mcp -o jsonpath='{.spec.host}')
```

### Network Policies

OpenShift uses OVN-Kubernetes for SDN.

#### Default Network Policy

```yaml
networkPolicy:
  enabled: true
  egress:
    - to:
      - namespaceSelector: {}
      ports:
      - protocol: TCP
        port: 53
      - protocol: UDP
        port: 53
    - to:
      - podSelector: {}
      ports:
      - protocol: TCP
        port: 443
```

#### Custom Network Policy

```bash
cat <<EOF | oc apply -f -
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: notebooklm-mcp-netpol
  namespace: notebooklm-mcp
spec:
  podSelector:
    matchLabels:
      app.kubernetes.io/name: notebooklm-mcp-openshift
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: openshift-ingress
    ports:
    - protocol: TCP
      port: 8080
  egress:
  - to:
    - namespaceSelector: {}
    ports:
    - protocol: TCP
      port: 53
    - protocol: UDP
      port: 53
  - to:
    - podSelector: {}
    ports:
    - protocol: TCP
      port: 443
    - protocol: TCP
      port: 80
EOF
```

#### Test Network Policy

```bash
# Check if policy is applied
oc get networkpolicy -n notebooklm-mcp

# Test connectivity from pod
oc rsh deployment/notebooklm-mcp

# Inside pod
curl -I https://notebooklm.google.com
```

### Service Mesh Integration

For advanced traffic management with OpenShift Service Mesh (Istio):

```yaml
# Enable sidecar injection
podAnnotations:
  sidecar.istio.io/inject: "true"
```

---

## Monitoring

### OpenShift Built-in Monitoring

Enable monitoring:

```yaml
monitoring:
  enabled: true
  serviceMonitor:
    enabled: true
    interval: 30s
```

#### View Metrics in Console

1. Navigate to OpenShift Console
2. Observe → Metrics
3. Query examples:
   ```promql
   # Memory usage
   container_memory_usage_bytes{container="notebooklm-mcp-openshift"}

   # CPU usage
   rate(container_cpu_usage_seconds_total{container="notebooklm-mcp-openshift"}[5m])

   # Pod count
   kube_deployment_status_replicas_available{deployment="notebooklm-mcp"}
   ```

#### Alerts

Enable PrometheusRule:

```yaml
monitoring:
  prometheusRule:
    enabled: true
```

View alerts:

```bash
# List PrometheusRules
oc get prometheusrule -n notebooklm-mcp

# View alerts in console
Observe → Alerting
```

### Custom Dashboards

Create Grafana dashboard in OpenShift:

1. Navigate to Observe → Dashboards
2. Import dashboard JSON
3. Use PromQL queries for visualization

---

## Troubleshooting

### Common Issues

#### 1. Pod Fails to Start

```bash
# Check pod status
oc get pods -n notebooklm-mcp

# Describe pod
oc describe pod -l app.kubernetes.io/name=notebooklm-mcp-openshift -n notebooklm-mcp

# Check events
oc get events -n notebooklm-mcp --sort-by='.lastTimestamp' | tail -20

# View logs
oc logs -f deployment/notebooklm-mcp -n notebooklm-mcp
```

**Common causes:**
- SCC violations → Check SCC binding
- Image pull errors → Verify image exists
- Resource limits → Check node resources

#### 2. PVC Not Binding

```bash
# Check PVC status
oc get pvc -n notebooklm-mcp

# Describe PVC
oc describe pvc notebooklm-mcp -n notebooklm-mcp

# Check storage class
oc get storageclass
```

**Solutions:**
```bash
# If no default storage class, set one
oc patch storageclass <storage-class-name> -p '{"metadata": {"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'

# Or specify in values
persistence:
  storageClass: "ocs-storagecluster-ceph-rbd"
```

#### 3. Route Not Accessible

```bash
# Check route
oc get route -n notebooklm-mcp

# Check route status
oc describe route notebooklm-mcp -n notebooklm-mcp

# Test from within cluster
oc run test --rm -it --image=curlimages/curl -- curl -I http://notebooklm-mcp:8080
```

#### 4. Authentication Issues

```bash
# Check if chrome-user-data is empty
oc rsh deployment/notebooklm-mcp
ls -la /app/chrome-user-data

# Re-run authentication
uv run python scripts/setup_auth.py
```

#### 5. SCC Violations

```bash
# Check pod security context
oc get pod -l app.kubernetes.io/name=notebooklm-mcp-openshift -o yaml | grep -A 10 securityContext

# Check which SCC is used
oc get pod -l app.kubernetes.io/name=notebooklm-mcp-openshift -o yaml | grep openshift.io/scc

# Grant SCC if needed
oc adm policy add-scc-to-user restricted-v2 -z notebooklm-mcp -n notebooklm-mcp
```

### Debug Mode

Enable debug logging:

```bash
# Update deployment
oc set env deployment/notebooklm-mcp LOG_LEVEL=DEBUG -n notebooklm-mcp

# View debug logs
oc logs -f deployment/notebooklm-mcp -n notebooklm-mcp

# Revert
oc set env deployment/notebooklm-mcp LOG_LEVEL=INFO -n notebooklm-mcp
```

### Performance Troubleshooting

```bash
# Check resource usage
oc adm top pod -l app.kubernetes.io/name=notebooklm-mcp-openshift -n notebooklm-mcp

# Check node resources
oc adm top nodes

# Describe node for resource allocation
oc describe node <node-name>
```

---

## Best Practices

### 1. Resource Management

```yaml
# Recommended settings
resources:
  requests:
    cpu: 1000m
    memory: 2Gi
  limits:
    cpu: 2000m
    memory: 3Gi
```

### 2. High Availability

```yaml
# Multi-replica with RWX storage
replicaCount: 3

persistence:
  storageClass: "ocs-storagecluster-cephfs"
  accessMode: ReadWriteMany

affinity:
  podAntiAffinity:
    preferredDuringSchedulingIgnoredDuringExecution:
    - weight: 100
      podAffinityTerm:
        labelSelector:
          matchLabels:
            app.kubernetes.io/name: notebooklm-mcp-openshift
        topologyKey: kubernetes.io/hostname
```

### 3. Security Hardening

```yaml
# Use minimal SCC
securityContext:
  sccName: "restricted-v2"

# Enable network policies
networkPolicy:
  enabled: true

# Use secrets for sensitive data
secret:
  enabled: true
```

### 4. Monitoring & Alerting

```yaml
monitoring:
  enabled: true
  serviceMonitor:
    enabled: true
  prometheusRule:
    enabled: true
```

### 5. Backup Strategy

```yaml
# Enable backup annotations
backup:
  enabled: true
  schedule: "0 2 * * *"
```

Regular backups:

```bash
# Weekly full backup
oc create -f backup-weekly.yaml

# Daily incremental
oc create -f backup-daily.yaml
```

### 6. Update Strategy

```bash
# Rolling update (zero downtime)
helm upgrade notebooklm-mcp ./helm/notebooklm-mcp-openshift \
  --set image.tag=v1.0.1 \
  --wait \
  --timeout 10m
```

### 7. Logging

Configure centralized logging with OpenShift Logging (EFK stack):

```bash
# Install OpenShift Logging operator
# Configure log forwarding to external systems
```

---

## Production Checklist

- [ ] Storage class configured and tested
- [ ] SCC properly configured
- [ ] Network policies applied
- [ ] Resource limits set appropriately
- [ ] Monitoring enabled (ServiceMonitor + PrometheusRule)
- [ ] Backup strategy implemented
- [ ] Authentication pre-configured
- [ ] Route with TLS enabled
- [ ] High availability configured (if needed)
- [ ] Documentation updated
- [ ] Disaster recovery plan
- [ ] Security scan completed
- [ ] Load testing performed

---

## Additional Resources

- [OpenShift 4.19 Documentation](https://docs.openshift.com/container-platform/4.19/)
- [OVN-Kubernetes Networking](https://docs.openshift.com/container-platform/4.19/networking/ovn_kubernetes_network_provider/about-ovn-kubernetes.html)
- [OpenShift Storage](https://docs.openshift.com/container-platform/4.19/storage/index.html)
- [SecurityContextConstraints](https://docs.openshift.com/container-platform/4.19/authentication/managing-security-context-constraints.html)
- [Routes](https://docs.openshift.com/container-platform/4.19/networking/routes/route-configuration.html)

---

**Questions or Issues?**
- GitHub Issues: https://github.com/yourusername/notebooklm-mcp/issues
- Documentation: https://github.com/yourusername/notebooklm-mcp

---

**Certified for OpenShift 4.19** ✅
