# Contributing to Flex001

Thank you for your interest in contributing to Flex001! This document provides guidelines for contributing to this industrial vision inspection system.

## 🎯 Project Overview

Flex001 is an industrial vision inspection system designed for:
- **Nail detection** in manufacturing processes
- **Board alignment measurement** using computer vision
- **Real-time fault logging** and hardware control
- **Industrial camera integration** with Basler cameras

## 🤝 How to Contribute

### Reporting Issues

Before creating an issue, please:
1. Check existing issues to avoid duplicates
2. Use the appropriate issue template
3. Provide detailed information including:
   - Operating system and Python version
   - Hardware configuration (cameras, relays)
   - Error messages and logs
   - Steps to reproduce the issue

### Feature Requests

When requesting features:
1. Describe the use case clearly
2. Explain the expected benefit
3. Consider if it aligns with the project's industrial focus
4. Provide examples if possible

### Code Contributions

#### Development Setup

1. **Fork the repository**
   ```bash
   git clone https://github.com/yourusername/Flex001.git
   cd Flex001
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

#### Coding Standards

- **Python Style**: Follow PEP 8 guidelines
- **Documentation**: Add docstrings to all functions and classes
- **Type Hints**: Use type hints for function parameters and return values
- **Logging**: Use the existing logging system for debugging
- **Error Handling**: Implement proper exception handling

#### Testing

- Test your changes thoroughly
- Ensure compatibility with existing hardware interfaces
- Test both CPU and GPU modes if applicable
- Verify camera and relay functionality

#### Commit Guidelines

Use conventional commit messages:
```
feat: add new camera calibration feature
fix: resolve relay communication timeout
docs: update installation instructions
refactor: improve detection worker performance
test: add unit tests for image processing
```

#### Pull Request Process

1. **Update documentation** if needed
2. **Add tests** for new functionality
3. **Update requirements.txt** if adding dependencies
4. **Test on different platforms** if possible
5. **Ensure all tests pass**
6. **Request review** from maintainers

## 🏗️ Project Structure

```
Flex001/
├── main.py                          # Application entry point
├── config/                          # Configuration management
├── utils/                           # Utility functions
├── hardware/                        # Hardware interfaces
├── database/                        # Database operations
├── models/                          # ML model management
├── camera/                          # Camera handling
├── detection/                       # Detection algorithms
└── gui/                            # User interface
```

## 🔧 Development Guidelines

### Hardware Integration

When working with hardware components:
- **Cameras**: Test with both hardware-triggered and timed modes
- **Relays**: Verify serial communication protocols
- **Safety**: Consider industrial safety implications
- **Error Handling**: Implement robust error recovery

### Performance Considerations

- **GPU Memory**: Monitor CUDA memory usage
- **Real-time Processing**: Maintain frame rate requirements
- **Database Operations**: Optimise for concurrent access
- **GUI Responsiveness**: Keep UI thread unblocked

### Security and Safety

- **Industrial Safety**: Consider safety implications of changes
- **Error Logging**: Ensure proper error tracking
- **Data Validation**: Validate all inputs and configurations
- **Hardware Safety**: Implement failsafe mechanisms

## 📝 Documentation

When contributing documentation:
- Use clear, concise language
- Include code examples where helpful
- Update both README.md and inline documentation
- Consider industrial users' needs

## 🐛 Bug Reports

When reporting bugs, include:
- **Environment**: OS, Python version, hardware setup
- **Steps**: Detailed reproduction steps
- **Expected vs Actual**: Clear description of the issue
- **Logs**: Relevant error messages and logs
- **Screenshots**: If applicable to GUI issues

## 📋 Issue Templates

### Bug Report Template
```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. See error

**Expected behavior**
A clear description of what you expected to happen.

**Environment:**
- OS: [e.g. Windows 10, Ubuntu 20.04]
- Python Version: [e.g. 3.9.7]
- Hardware: [e.g. Basler camera model, relay type]

**Additional context**
Add any other context about the problem here.
```

### Feature Request Template
```markdown
**Is your feature request related to a problem?**
A clear description of what the problem is.

**Describe the solution you'd like**
A clear description of what you want to happen.

**Describe alternatives you've considered**
A clear description of any alternative solutions.

**Additional context**
Add any other context or screenshots about the feature request.
```

## 📞 Contact

For questions about contributing:
- **Email**: [Your email]
- **Phone**: Sam Smith - 07948607918

## 📄 License

By contributing to Flex001, you agree that your contributions will be licensed under the GNU General Public License v3 (GPLv3).

## 🙏 Acknowledgments

Thank you to all contributors who help make Flex001 better for the industrial vision community! 