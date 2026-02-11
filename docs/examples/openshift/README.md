# OpenShift Deployment Example

This directory contains example files from testing the NotebookLM MCP server on OpenShift.

## Files

- **values-test.yaml**: Example Helm values for OpenShift deployment
  - Configures BuildConfig to build from GitHub
  - Sets up storage with OCS/Ceph RBD
  - Includes HTTP transport environment variables

- **deployment-summary.md**: Notes from OpenShift deployment testing
  - Documents the deployment process
  - Records any issues encountered
  - Testing results

## Usage

These files serve as **reference examples** for experimental OpenShift deployments.

⚠️ **Note**: OpenShift deployment is experimental and not recommended for multi-user production use. See [OPENSHIFT_DEPLOYMENT.md](../../OPENSHIFT_DEPLOYMENT.md) for details.

### Example Deployment

```bash
# From the main project directory
helm install notebooklm-test ./helm/notebooklm-mcp-openshift \
  -f docs/examples/openshift/values-test.yaml \
  -n your-namespace
```

## Related Documentation

- [OpenShift Deployment Guide](../../OPENSHIFT_DEPLOYMENT.md)
- [Deployment Guide](../../README_DEPLOYMENT.md)
