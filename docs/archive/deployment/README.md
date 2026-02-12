# Deployment Documentation (Archived)

This folder contains documentation for experimental containerized deployments of the NotebookLM MCP server. These are **not the primary use case** for this project.

## Primary Use Case: Claude Code

The NotebookLM MCP server is designed for **local use with Claude Code**. See the main README.md and CLAUDE_CODE_SETUP.md for the recommended setup.

## Experimental Deployments

The documentation in this folder covers:

- **Containerization**: Building and running in containers (Podman/Docker)
- **Kubernetes**: Deploying to Kubernetes clusters
- **OpenShift**: Deploying to Red Hat OpenShift
- **Multi-architecture builds**: ARM64/AMD64 support

These deployments are **experimental** and face challenges:
- Each user needs their own Google account session
- No official NotebookLM API for programmatic authentication
- Browser automation is designed for single-user scenarios
- Significant complexity for session isolation and management

## Available Documentation

- `CONTAINERIZATION_SUMMARY.md` - Container deployment overview
- `README_DEPLOYMENT.md` - Kubernetes deployment guide
- `OPENSHIFT_DEPLOYMENT.md` - OpenShift deployment guide
- `OPENSHIFT_SUMMARY.md` - OpenShift summary
- `OPENSHIFT_QUICK_REFERENCE.md` - OpenShift quick commands
- `CRC_DEPLOYMENT_NOTES.md` - CodeReady Containers notes
- `CRC_DEPLOYMENT_SUCCESS.md` - CRC deployment success
- `MULTI_ARCH_BUILD.md` - Multi-architecture build guide
- `QUICK_REFERENCE.md` - Quick reference for deployments

## Recommendation

For the best experience, use the NotebookLM MCP server **locally with Claude Code** as described in the main documentation.
