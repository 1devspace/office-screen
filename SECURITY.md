# Security Policy

## Supported Versions

We provide security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 2.0.x   | :white_check_mark: |
| < 2.0   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability, please **do not** open a public issue.

Instead, please report it via one of the following methods:

1. **Email**: Send details to the maintainers (check repository for contact info)
2. **Private Security Advisory**: Use GitHub's private vulnerability reporting feature if available

### What to Include

When reporting a vulnerability, please include:

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if you have one)
- Your contact information

### Response Timeline

- **Initial Response**: Within 48 hours
- **Status Update**: Within 7 days
- **Fix Timeline**: Depends on severity, but we aim for quick resolution

## Security Best Practices

When using office_screen:

1. **Keep dependencies updated**: Regularly update Python packages
2. **Use secure URLs**: Only browse trusted websites
3. **Review configurations**: Check config files before use
4. **Monitor logs**: Regularly check logs for suspicious activity
5. **Use proxies carefully**: If using proxies, ensure they're from trusted sources

## Known Security Considerations

- The tool uses Selenium WebDriver which requires Chrome/ChromeDriver
- Browser automation can be detected by websites
- User agents and proxies should be used responsibly
- Ensure compliance with website terms of service

## Disclosure Policy

- Vulnerabilities will be disclosed after a fix is available
- Credit will be given to reporters (if desired)
- We follow responsible disclosure practices

Thank you for helping keep office_screen secure!
