# 🚧 GitHub Actions Workflows - Temporarily Disabled

The CI/CD workflows have been temporarily disabled during initial development setup.

## Disabled Workflows

- `ci-cd.yml.disabled` - Main CI/CD pipeline (tests, security, docker build)
- `ci.yml.disabled` - Continuous Integration tests
- `dependency-update.yml.disabled` - Automated dependency updates

## Why Disabled?

These workflows require:
1. Complete project structure with actual code
2. Proper test files in `/tests` directory
3. All dependencies properly configured
4. Database migrations set up
5. Environment variables configured

## Re-enabling Workflows

When ready to enable CI/CD, simply rename the files back:

```bash
mv ci-cd.yml.disabled ci-cd.yml
mv ci.yml.disabled ci.yml
mv dependency-update.yml.disabled dependency-update.yml
```

## What Each Workflow Does

### CI/CD Pipeline (`ci-cd.yml`)
- Runs tests with PostgreSQL and Redis
- Security scanning with bandit and safety
- Code quality checks (flake8, black)
- Builds and pushes Docker images
- Coverage reporting

### CI (`ci.yml`)
- Basic continuous integration tests
- Faster feedback for pull requests

### Dependency Update (`dependency-update.yml`)
- Automated dependency updates
- Creates PRs for security updates

---

**Status**: 🔴 Disabled until project setup is complete
