# Contributing to office_screen

Thank you for your interest in contributing to office_screen! This document provides guidelines and instructions for contributing.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for all contributors.

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/1devspace/office-screen/issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Python version, etc.)
   - Error messages or logs if applicable

### Suggesting Features

1. Check if the feature has already been suggested
2. Create a new issue with:
   - Clear description of the feature
   - Use case and benefits
   - Possible implementation approach (if you have ideas)

### Pull Requests

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow the code style (see below)
   - Add tests for new features
   - Update documentation as needed

4. **Test your changes**
   ```bash
   python3 -m pytest tests/
   ```

5. **Commit your changes**
   ```bash
   git commit -m "Add: description of your changes"
   ```
   Use clear, descriptive commit messages.

6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request**
   - Provide a clear description
   - Reference any related issues
   - Wait for review and feedback

## Code Style

- Follow PEP 8 style guide
- Use type hints where appropriate
- Write docstrings for all functions and classes
- Keep functions focused and small
- Use meaningful variable names

## Testing

- Write tests for all new features
- Ensure all existing tests pass
- Aim for good test coverage
- Use pytest for testing

## Documentation

- Update README.md for user-facing changes
- Add docstrings to new functions/classes
- Update inline comments for complex logic

## Development Setup

1. Clone your fork:
   ```bash
   git clone https://github.com/your-username/office-screen.git
   cd office-screen
   ```

2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install pytest pytest-cov  # For testing
   ```

4. Install in development mode:
   ```bash
   pip install -e .
   ```

## Commit Message Guidelines

Use clear, descriptive commit messages:

- `Add: feature description` - for new features
- `Fix: bug description` - for bug fixes
- `Update: what was updated` - for updates
- `Refactor: what was refactored` - for code refactoring
- `Docs: what documentation was changed` - for documentation
- `Test: what tests were added/changed` - for tests

## Questions?

Feel free to open an issue for questions or discussions!

Thank you for contributing! 🎉

