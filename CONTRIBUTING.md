# 🤝 Contributing to CronoExplorer

Thank you for your interest in contributing to CronoExplorer! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Basic knowledge of Flask, Web3.py, and blockchain concepts

### Development Setup

1. **Fork the repository**
   ```bash
   git clone https://github.com/yourusername/CronoExplorer.git
   cd CronoExplorer
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create a development branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

## 📝 Development Guidelines

### Code Style

- Follow PEP 8 Python style guidelines
- Use meaningful variable and function names
- Add docstrings for all public functions and classes
- Keep functions focused and single-purpose
- Maximum line length: 120 characters

### Testing

- Write tests for new functionality
- Ensure all existing tests pass
- Run the test suite before submitting:
  ```bash
  python tests.py
  ```

### Commit Messages

Use clear, descriptive commit messages:

```
feat: add support for new token standard
fix: resolve transaction classification error
docs: update installation instructions
style: improve button alignment
refactor: optimize RPC call performance
```

### Pull Request Process

1. **Create a feature branch** from `main`
2. **Make your changes** following the guidelines above
3. **Test thoroughly** - ensure no regressions
4. **Update documentation** if needed
5. **Submit a pull request** with a clear description

## 🎯 Areas for Contribution

### High Priority

- **Performance improvements** for RPC calls
- **Additional token standards** support
- **Better error handling** and user feedback
- **Mobile responsiveness** improvements

### Medium Priority

- **Additional blockchain networks** support
- **Enhanced transaction visualization**
- **Export functionality** (CSV, JSON)
- **API endpoints** for external integration

### Low Priority

- **Additional UI themes**
- **Internationalization** support
- **Advanced analytics** and charts
- **Plugin system** for custom classifiers

## 🧪 Testing

### Running Tests

```bash
# Run all tests
python tests.py

# Run specific test functions
python -c "from tests import test_classifier_full; test_classifier_full()"
```

### Test Coverage

- Aim for at least 80% test coverage
- Test both success and failure scenarios
- Mock external dependencies (RPC calls)
- Test edge cases and error conditions

## 🔧 Development Tools

### Recommended IDEs

- **VS Code** with Python extensions
- **PyCharm** Community or Professional
- **Vim/Neovim** with Python plugins

### Useful Extensions

- Python
- Flask
- YAML
- GitLens
- Python Test Explorer

## 📚 Documentation

### Code Documentation

- Use docstrings for all public functions
- Include examples in docstrings
- Document complex algorithms
- Keep README.md up to date

### API Documentation

- Document all Flask routes
- Include request/response examples
- Document error codes and messages
- Keep API docs synchronized with code

## 🐛 Bug Reports

### Before Reporting

1. Check if the issue is already reported
2. Try to reproduce the issue
3. Check the logs for error messages
4. Verify your configuration

### Bug Report Template

```
**Description**
Brief description of the issue

**Steps to Reproduce**
1. Step 1
2. Step 2
3. Step 3

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**Environment**
- OS: [e.g., Ubuntu 20.04]
- Python: [e.g., 3.9.7]
- CronoExplorer: [e.g., v1.0.0]
- Chain: [e.g., Cronos]

**Additional Information**
Any other relevant details
```

## 💡 Feature Requests

### Before Requesting

1. Check if the feature already exists
2. Consider if it fits the project scope
3. Think about implementation complexity
4. Consider maintenance burden

### Feature Request Template

```
**Feature Description**
Clear description of the requested feature

**Use Case**
Why this feature is needed

**Proposed Implementation**
How you think it could be implemented

**Alternatives Considered**
Other approaches you've considered

**Additional Context**
Any other relevant information
```

## 🏷️ Release Process

### Versioning

We use [Semantic Versioning](https://semver.org/):

- **MAJOR**: Breaking changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

### Release Checklist

- [ ] All tests pass
- [ ] Documentation updated
- [ ] Changelog updated
- [ ] Version numbers updated
- [ ] Release notes prepared
- [ ] GitHub release created

## 📞 Getting Help

### Communication Channels

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and discussions
- **Pull Requests**: For code reviews and feedback

### Code of Conduct

- Be respectful and inclusive
- Focus on the code, not the person
- Provide constructive feedback
- Help others learn and grow

## 🙏 Recognition

Contributors will be recognized in:

- Project README.md
- Release notes
- GitHub contributors page
- Project documentation

---

**Thank you for contributing to CronoExplorer! 🚀**
