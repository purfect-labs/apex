# 🚀 Shadow Testing Quick Reference

## Prerequisites Checklist

- [ ] APEX server is running: `python3 apex.py --web`
- [ ] Admin interface accessible: http://localhost:8000/static/admin.html
- [ ] Node.js and npm installed
- [ ] Playwright installed: `npm install @playwright/test`

## Common Commands

```bash
# Validate setup
./run-shadow-tests.sh validate

# Run all tests in parallel (6 workers) - FAST! 
./run-shadow-tests.sh parallel
./run-shadow-tests.sh all

# Run specific validation layers
./run-shadow-tests.sh ui          # UI elements only
./run-shadow-tests.sh auth        # Provider auth & contexts only

# Run specific provider (with 6 workers)
./run-shadow-tests.sh aws
./run-shadow-tests.sh gcp
./run-shadow-tests.sh kubernetes

# Generate HTML report (parallel)
./run-shadow-tests.sh report
```

## Test Files Quick Reference

| Provider | Test File | Coverage |
|----------|-----------|----------|
| AWS | `tests/aws-provider.shadow.spec.js` | Auth, environments, S3/EC2/RDS |
| GCP | `tests/gcp-provider.shadow.spec.js` | Auth, projects, Compute/Storage |
| K8s | `tests/kubernetes-provider.shadow.spec.js` | Contexts, kubectl commands |

## Troubleshooting

**Server not running?**
```bash
cd /Users/shawn_meredith/code/github/apex
python3 apex.py --web &
```

**Test failures?**
- Check network connectivity
- Verify cloud provider authentication
- Review logs with "WARP-DEMO" tags

**Need debug info?**
- Screenshots saved in `shadow-reports/`
- Console logs show detailed execution
- HTML reports at `shadow-reports/html/index.html`

## Test Results

- **Console**: Real-time progress with WARP-DEMO tags
- **HTML**: `shadow-reports/html/index.html` 
- **JSON**: `shadow-reports/results.json`
- **JUnit**: `shadow-reports/junit.xml`