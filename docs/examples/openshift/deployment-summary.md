# NotebookLM MCP OpenShift Deployment Test

## Test Environment
- **Cluster API:** https://api.cluster-zf77k.dynamic.redhatworkshops.io:6443
- **User:** system:serviceaccount:openshift-config:cluster-admin
- **Namespace:** notebooklm-mcp-test
- **Date:** $(date)

## Deployment Details

### Helm Release
- **Name:** notebooklm-test
- **Chart:** notebooklm-mcp-openshift
- **Version:** 0.1.0
- **Status:** Deployed

### Configuration Overrides
\`\`\`yaml
persistence:
  storageClass: "ocs-external-storagecluster-ceph-rbd"
  size: 2Gi

buildConfig:
  enabled: true
  git:
    uri: "https://github.com/yosri-rh/notebooklm-mcp.git"
    ref: "main"
  strategy: "docker"
\`\`\`

## Resources Created

### Storage
- **PVC:** notebooklm-test-notebooklm-mcp-openshift
- **Size:** 2Gi
- **Storage Class:** ocs-external-storagecluster-ceph-rbd (default)
- **Status:** Bound ✓

### Build
- **BuildConfig:** notebooklm-test-notebooklm-mcp-openshift
- **Strategy:** Docker
- **Source:** Git (GitHub main branch)
- **Status:** Running (in progress)

### Deployment
- **Name:** notebooklm-test-notebooklm-mcp-openshift
- **Replicas:** 1
- **Image:** Built from source via BuildConfig
- **Status:** Waiting for image build to complete

### Networking
- **Service:** notebooklm-test-notebooklm-mcp-openshift (ClusterIP: 172.231.221.242:8080)
- **Route:** notebooklm-test-notebooklm-mcp-openshift-notebooklm-mcp-test.apps.cluster-zf77k.dynamic.redhatworkshops.io
- **TLS:** Edge termination with redirect

## Testing Steps

1. ✅ Successfully logged into OpenShift cluster
2. ✅ Created test namespace: notebooklm-mcp-test  
3. ✅ Deployed Helm chart with custom values
4. ✅ PVC bound successfully
5. 🔄 Build in progress (installing system packages)
6. ⏳ Pod deployment pending (waiting for image)
7. ⏳ Authentication setup required after deployment

## Current Status Summary

✅ Successfully completed:
1. OpenShift cluster login with admin access
2. Created test namespace: notebooklm-mcp-test
3. BuildConfig successfully built container image in 3m4s
4. Image pushed to internal registry
5. PVC bound successfully
6. Deployment created with correct image reference

⚠️ Architectural limitation discovered:
- The notebooklm-mcp server uses MCP stdio transport
- Designed for local use with Claude Desktop or MCP Inspector
- Not compatible with long-running Kubernetes pod deployment
- Pod runs but exits immediately (CrashLoopBackOff)

## Potential Solutions

To make this work in OpenShift, one of the following approaches is needed:

### Option 1: Add HTTP/SSE Transport Support (Recommended)
- Modify `src/notebooklm_mcp/server.py` to support FastMCP's SSE transport
- This would allow the server to run as an HTTP service
- Clients could connect via HTTP instead of stdio
- Compatible with Kubernetes Service/Route model

### Option 2: Add Keep-Alive Wrapper
- Create a wrapper script that keeps stdin open
- Use `tail -f /dev/null` or similar to prevent container exit
- Clients would need to exec into the pod to use the MCP server
- Less ideal but simpler to implement

### Option 3: Job-Based Model
- Deploy as a Kubernetes Job instead of Deployment
- Run on-demand rather than as a long-running service
- Would require different Helm chart architecture

## Testing Results

| Component | Status | Notes |
|-----------|--------|-------|
| Cluster Access | ✅ | Successfully logged in with admin token |
| Namespace | ✅ | notebooklm-mcp-test created |
| Storage | ✅ | 2Gi PVC bound with ocs-external-storagecluster-ceph-rbd |
| BuildConfig | ✅ | Image built and pushed in 3m4s |
| ImageStream | ✅ | Created and tagged with 'latest' |
| Deployment | ⚠️ | Created but pods crash due to stdio transport |
| Service | ✅ | Created (ClusterIP 172.231.221.242:8080) |
| Route | ✅ | Created with TLS edge termination |
| Application | ❌ | Not running - architectural limitation |

## Next Steps for Production Use

1. **Decide on transport mode:**
   - Implement HTTP/SSE support in the MCP server for true Kubernetes deployment
   - OR: Document that this is a local-only tool and remove OpenShift deployment

2. **If implementing HTTP/SSE:**
   - Research FastMCP SSE transport capabilities
   - Modify server.py to support both stdio and SSE modes
   - Update Containerfile command/args to enable SSE mode
   - Test with HTTP clients instead of Claude Desktop

3. **Alternative:**
   - Use this Helm chart to deploy the container for development purposes
   - Access the MCP server via `oc rsh` for interactive use
   - Not recommended for production workloads

## Issues Encountered

### Issue 1: Storage Class Not Found
- **Problem:** Initial deployment used storage class "ocs-storagecluster-ceph-rbd" which doesn't exist
- **Solution:** Updated to use "ocs-external-storagecluster-ceph-rbd" (default storage class)
- **Status:** Resolved ✓

### Issue 2: Image Pull Error (Wrong Repository)
- **Problem:** Deployment trying to pull from `notebooklm-mcp/notebooklm-mcp:latest` but BuildConfig pushed to `notebooklm-mcp-test/notebooklm-test-notebooklm-mcp-openshift:latest`
- **Solution:** Updated values-test.yaml to override image repository to match the ImageStream created by BuildConfig
- **Status:** Resolved ✓

### Issue 3: Pod CrashLoopBackOff - Architectural Limitation
- **Problem:** Pod keeps restarting (currently RESTARTS: 2) because MCP server exits immediately
- **Root Cause:** The MCP server uses stdio transport, designed for Claude Desktop/MCP Inspector:
  - When run in a Kubernetes pod, stdin closes immediately (no connected client)
  - The stdio-based MCP server detects EOF and exits
  - Kubernetes restarts the pod, cycle repeats
- **Details:**
  - Containerfile ENTRYPOINT: `/app/.venv/bin/python -m notebooklm_mcp.server`
  - Server starts: "Starting MCP server 'notebooklm' with transport 'stdio'"
  - Then immediately exits when stdin closes
  - Helm chart exposes port 8080 for HTTP, but MCP server only listens on stdio
- **Status:** Architectural limitation - requires code changes to fix properly

## Commands for Monitoring

\`\`\`bash
# Check build status
oc get builds -n notebooklm-mcp-test

# Watch build logs
oc logs -f build/notebooklm-test-notebooklm-mcp-openshift-1 -n notebooklm-mcp-test

# Check pod status
oc get pods -n notebooklm-mcp-test

# View all resources
oc get all -n notebooklm-mcp-test

# Get route URL
oc get route -n notebooklm-mcp-test
\`\`\`
