# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability, please follow these steps:

### 1. Do Not Open a Public Issue

Please **do not** open a public GitHub issue for security vulnerabilities.

### 2. Contact Us Privately

Send an email to: **security@yourdomain.com** (replace with your email)

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### 3. Response Timeline

- **Initial Response**: Within 48 hours
- **Status Update**: Within 7 days
- **Fix Timeline**: Depends on severity
  - Critical: Within 7 days
  - High: Within 14 days
  - Medium: Within 30 days
  - Low: Next release cycle

## Security Best Practices

### Authentication

- **Never commit** `chrome-user-data/` to version control
- **Rotate credentials** periodically
- **Use secrets management** for production deployments
- **Limit access** to authentication data

### Docker Security

- **Run as non-root user** (implemented by default)
- **Use specific image tags** instead of `latest` in production
- **Scan images** for vulnerabilities regularly
- **Enable security contexts** in Kubernetes

### Kubernetes Security

```yaml
# Recommended security settings
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  fsGroup: 1000
  allowPrivilegeEscalation: false
  capabilities:
    drop:
    - ALL
  seccompProfile:
    type: RuntimeDefault
```

### Network Security

- **Use private container registries**
- **Restrict network access** to necessary endpoints only
- **Enable TLS/SSL** for all communications
- **Use network policies** in Kubernetes

### Secrets Management

**Don't:**
```yaml
# ❌ Never put secrets in ConfigMaps
apiVersion: v1
kind: ConfigMap
data:
  password: "mysecret123"
```

**Do:**
```yaml
# ✅ Use Kubernetes Secrets
apiVersion: v1
kind: Secret
type: Opaque
data:
  password: bXlzZWNyZXQxMjM=  # base64 encoded
```

Or use external secret managers:
- AWS Secrets Manager
- HashiCorp Vault
- Azure Key Vault
- Google Secret Manager

## Known Security Considerations

### Browser Automation Risks

This project uses Playwright for browser automation:

1. **Cookie/Session Theft**: Chrome user data contains authentication cookies
   - **Mitigation**: Encrypt volumes, restrict access, use short-lived sessions

2. **Screen Recording**: Headless=false can be monitored
   - **Mitigation**: Always use headless mode in production

3. **Man-in-the-Middle**: Network traffic can be intercepted
   - **Mitigation**: Use trusted networks, enable VPN if needed

### NotebookLM Terms of Service

⚠️ **Important**: This tool automates interaction with Google NotebookLM, which may violate their Terms of Service.

- **Use responsibly** and for personal/educational purposes only
- **Respect rate limits** to avoid account suspension
- **Monitor for policy changes** from Google
- **This is not an official Google product**

### Container Security

The Docker image includes:
- Chromium browser and dependencies
- Python runtime
- System libraries

Regular updates are needed for:
- Security patches
- Dependency updates
- OS updates

### Data Privacy

This application:
- **Stores authentication data** locally in chrome-user-data/
- **Accesses your Google account** to interact with NotebookLM
- **Sends data to Google** services

Ensure compliance with:
- GDPR (if applicable)
- Your organization's data policies
- Google's privacy policy

## Security Checklist for Deployment

### Before Deployment

- [ ] Review and customize security contexts
- [ ] Set up secrets management
- [ ] Configure network policies
- [ ] Enable audit logging
- [ ] Set resource limits
- [ ] Configure RBAC appropriately
- [ ] Review image for vulnerabilities
- [ ] Document authentication process

### After Deployment

- [ ] Verify security settings
- [ ] Test authentication flow
- [ ] Monitor logs for suspicious activity
- [ ] Set up alerts for failures
- [ ] Regular security audits
- [ ] Keep dependencies updated
- [ ] Backup authentication data securely

## Vulnerability Scanning

### Container Images

```bash
# Scan with Trivy
trivy image notebooklm-mcp:latest

# Scan with Docker Scout
docker scout cves notebooklm-mcp:latest
```

### Dependencies

```bash
# Python dependencies
pip-audit

# Or with safety
safety check
```

## Updates and Patching

- **Subscribe** to security advisories
- **Update dependencies** regularly
- **Rebuild images** monthly minimum
- **Test updates** before production deployment
- **Have rollback plan** ready

## Responsible Disclosure

We believe in responsible disclosure:

1. Report vulnerability privately
2. Allow time for fix
3. Coordinate disclosure timing
4. Credit security researchers

## Security Resources

- [OWASP Container Security](https://owasp.org/www-project-docker-top-10/)
- [Kubernetes Security Best Practices](https://kubernetes.io/docs/concepts/security/)
- [CIS Docker Benchmark](https://www.cisecurity.org/benchmark/docker)
- [CIS Kubernetes Benchmark](https://www.cisecurity.org/benchmark/kubernetes)

## Contact

For security issues: security@yourdomain.com
For general issues: https://github.com/yourusername/notebooklm-mcp/issues

---

**Note**: This is an educational/personal project. Use at your own risk. The maintainers are not responsible for any security incidents or violations of third-party terms of service.
