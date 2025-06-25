# GitHub Actions Workflows

This document describes all the GitHub Actions workflows configured for the Pi-Pages project.

## Overview

The project uses a comprehensive CI/CD pipeline with multiple specialized workflows:

- **Continuous Integration (CI)**: Orchestrates all quality checks
- **Testing**: Unit and integration tests with coverage
- **Security**: Vulnerability scanning and security analysis
- **Code Quality**: Formatting, linting, and type checking
- **Performance**: Benchmarks and load testing
- **Documentation**: Build and deploy documentation
- **Docker**: Container build and testing
- **Release**: Package building and publishing
- **Dependency Updates**: Automated dependency management

## Workflow Details

### 1. Continuous Integration (`ci.yml`)

**Trigger**: `push`, `pull_request`

**Purpose**: Main orchestrator workflow that runs all quality checks in parallel.

**Jobs**:
- `quick-checks`: Fast syntax and formatting checks
- `test`: Unit and integration tests
- `security`: Security vulnerability scanning
- `code-quality`: Code formatting and linting
- `performance`: Performance benchmarks
- `documentation`: Documentation building
- `docker`: Docker image testing
- `summary`: Aggregates results and comments on PRs

**Features**:
- Parallel execution for faster feedback
- Comprehensive status reporting
- Automatic PR comments with results summary

### 2. Testing (`test.yml`)

**Trigger**: `push`, `pull_request`

**Purpose**: Comprehensive testing with multiple Python versions and Selenium.

**Features**:
- Matrix testing across Python 3.8-3.11
- Selenium Chrome service for browser testing
- Coverage reporting with Codecov integration
- Test artifacts for debugging
- Integration test support

**Requirements**:
- Chrome browser service
- Test files in `tests/` directory

### 3. Security (`security.yml`)

**Trigger**: `push`, `pull_request`, `schedule`

**Purpose**: Security vulnerability scanning and analysis.

**Tools**:
- **Bandit**: Python security linter
- **Safety**: Dependency vulnerability checker

**Features**:
- JSON and text report generation
- Automatic PR comments with security findings
- Scheduled weekly scans
- Artifact uploads for detailed analysis

### 4. Code Quality (`code-quality.yml`)

**Trigger**: `push`, `pull_request`

**Purpose**: Code formatting, import sorting, and style checking.

**Tools**:
- **Black**: Code formatter
- **isort**: Import sorter
- **flake8**: Style checker
- **mypy**: Type checker

**Features**:
- Automatic formatting fixes
- Auto-generated PRs for formatting issues
- Consistent code style enforcement

### 5. Performance (`performance.yml`)

**Trigger**: `push`, `pull_request`, `schedule`

**Purpose**: Performance benchmarking and load testing.

**Features**:
- Memory profiling
- Performance benchmarks
- Load testing
- Performance regression detection
- Automated performance reports

### 6. Documentation (`documentation.yml`)

**Trigger**: `push`, `pull_request`

**Purpose**: Documentation building and deployment.

**Features**:
- Sphinx documentation generation
- Link validation
- GitHub Pages deployment
- Documentation artifacts

### 7. Docker (`docker.yml`)

**Trigger**: `push`, `pull_request`

**Purpose**: Docker image building and testing.

**Features**:
- Multi-platform Docker builds
- Docker Hub integration
- Containerized testing
- Image validation

### 8. Release (`release.yml`)

**Trigger**: `push` with tags (`v*`)

**Purpose**: Package building and publishing.

**Features**:
- Multi-Python version testing
- PyPI publishing
- GitHub release creation
- Package validation

### 9. Dependency Updates (`dependency-update.yml`)

**Trigger**: `schedule` (weekly), `workflow_dispatch`

**Purpose**: Automated dependency management.

**Features**:
- Weekly dependency checks
- Automatic PR creation for updates
- Manual trigger support
- Dependency security scanning

## Configuration

### Required Secrets

For full functionality, configure these repository secrets:

```bash
# PyPI Publishing
PYPI_API_TOKEN=your_pypi_token

# Docker Hub
DOCKERHUB_USERNAME=your_dockerhub_username
DOCKERHUB_TOKEN=your_dockerhub_token

# Codecov (optional)
CODECOV_TOKEN=your_codecov_token
```

### Environment Variables

Some workflows use environment variables for configuration:

```yaml
# Example environment configuration
env:
  PYTHONPATH: .
  SELENIUM_HEADLESS: true
  CHROME_OPTIONS: --no-sandbox --disable-dev-shm-usage
```

## Usage

### Local Development

To run the same checks locally:

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run all quality checks
black --check .
isort --check-only .
flake8 .
mypy .
bandit -r .
safety check

# Run tests
pytest tests/ -v --cov=pi_pages

# Run performance tests
pytest tests/performance/ -v --benchmark-only
```

### Workflow Triggers

**Automatic Triggers**:
- `push`: Runs on all pushes to any branch
- `pull_request`: Runs on PR creation and updates
- `schedule`: Weekly security and dependency checks

**Manual Triggers**:
- `workflow_dispatch`: Manual workflow execution
- Tag creation: Triggers release workflow

### Workflow Status

Monitor workflow status:

1. **GitHub Actions Tab**: View all workflow runs
2. **PR Comments**: Automatic status updates
3. **Status Badges**: Add to README for quick status

## Customization

### Adding New Workflows

1. Create `.github/workflows/your-workflow.yml`
2. Follow the existing pattern
3. Add to CI orchestration if needed
4. Update documentation

### Modifying Existing Workflows

1. Edit the specific workflow file
2. Test changes in a branch
3. Update this documentation
4. Consider backward compatibility

### Workflow Optimization

**Performance Tips**:
- Use caching for dependencies
- Parallel job execution
- Conditional job skipping
- Resource optimization

**Cost Optimization**:
- Limit concurrent jobs
- Use self-hosted runners for heavy workloads
- Optimize Docker layer caching
- Remove unnecessary steps

## Troubleshooting

### Common Issues

1. **Workflow Failures**:
   - Check job logs for specific errors
   - Verify secret configuration
   - Test locally with same environment

2. **Performance Issues**:
   - Review resource usage
   - Optimize Docker images
   - Use caching effectively

3. **Security Warnings**:
   - Review Bandit/Safety reports
   - Update vulnerable dependencies
   - Address false positives

### Debugging

1. **Enable Debug Logging**:
   ```yaml
   env:
     ACTIONS_STEP_DEBUG: true
     ACTIONS_RUNNER_DEBUG: true
   ```

2. **Local Testing**:
   - Use `act` for local workflow testing
   - Test individual steps locally
   - Validate configuration files

3. **Artifact Analysis**:
   - Download workflow artifacts
   - Review generated reports
   - Check coverage and test results

## Best Practices

1. **Workflow Design**:
   - Keep workflows focused and single-purpose
   - Use reusable workflows for common patterns
   - Implement proper error handling

2. **Security**:
   - Use minimal required permissions
   - Rotate secrets regularly
   - Scan for vulnerabilities

3. **Performance**:
   - Cache dependencies and build artifacts
   - Use matrix builds efficiently
   - Optimize Docker images

4. **Maintenance**:
   - Regular dependency updates
   - Monitor workflow performance
   - Update documentation

## Support

For workflow issues:

1. Check the [GitHub Actions documentation](https://docs.github.com/en/actions)
2. Review workflow logs for specific errors
3. Test changes in a separate branch
4. Create issues for persistent problems

## Contributing

When contributing to workflows:

1. Follow existing patterns and conventions
2. Test changes thoroughly
3. Update documentation
4. Consider impact on CI/CD pipeline
5. Ensure backward compatibility 