# Development Standards & Workflow

## 🌐 **Language Standards**

### English-Only Policy
All technical content must be written in **English** to maintain professional standards and consistency:

- ✅ **Commit messages** - Use conventional commit format
- ✅ **Documentation files** (*.md) - All technical docs in English  
- ✅ **Code comments** - English comments for better readability
- ✅ **Variable names** - English naming conventions
- ✅ **Function names** - Descriptive English names
- ✅ **Log messages** - Consistent English logging

### Exception
- User-facing messages in Indonesian UI can remain in Indonesian
- Configuration descriptions for local users

## 📝 **Commit Message Standards**

### Conventional Commit Format
```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### Types
- `feat`: New feature
- `fix`: Bug fix  
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Examples
```bash
feat(monitoring): add real-time data visualization dashboard
fix(serial): resolve MockSerial initialization error in demo mode  
docs(deployment): update installation guide with systemctl-free options
refactor(watchdog): improve singleton protection mechanism
```

## 🔄 **Git Workflow**

### Dual Repository Push
Always push to **both repositories**:

```bash
# Manual method
git push origin main
git push upstream main

# Automated method (recommended)
./push-both-remotes.sh
```

### Repository Structure
- **Origin**: `git@github.com:StefanusSimandjuntak111/roll-machine-monitor.git`
- **Upstream**: `git@github.com:hokgt/textilindo_roll_printer.git`

### Workflow Steps
1. Make changes and test locally
2. Write descriptive commit message in English
3. Commit changes: `git commit -m "feat: add new feature"`
4. Push to both remotes: `./push-both-remotes.sh`
5. Create documentation if needed

## 📁 **File Naming Standards**

### Documentation Files
- Use UPPERCASE for major documentation: `README.md`, `CHANGELOG.md`
- Use descriptive names: `INSTALLATION_GUIDE.md`, `API_REFERENCE.md`
- Version-specific docs: `RELEASE_NOTES_v1.2.3.md`

### Code Files
- Use snake_case for Python: `serial_handler.py`, `main_window.py`
- Use kebab-case for scripts: `smart-watchdog.sh`, `deploy-script.sh`
- Use PascalCase for classes: `SerialHandler`, `MainWindow`

## 🏗️ **Code Structure Standards**

### Python Code Quality
1. **PEP 8** compliance for style
2. **Type hints** for all functions
3. **Docstrings** for all public methods
4. **Error handling** with proper logging
5. **Unit tests** for critical functionality

### Documentation Structure
```
PROJECT_ROOT/
├── README.md                 # Main project overview
├── INSTALLATION.md          # Installation instructions  
├── DEVELOPMENT_STANDARDS.md # This file
├── CHANGELOG.md             # Version history
├── docs/                    # Additional documentation
│   ├── API_REFERENCE.md
│   ├── TROUBLESHOOTING.md
│   └── DEPLOYMENT_GUIDE.md
└── scripts/                 # Utility scripts
    ├── push-both-remotes.sh
    └── prepare-deployment.sh
```

## 🚀 **Release Process**

### Version Numbering
Use [Semantic Versioning](https://semver.org/): `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)  
- **PATCH**: Bug fixes (backward compatible)

### Release Steps
1. Update version numbers
2. Update CHANGELOG.md
3. Create release documentation
4. Test deployment package
5. Tag release: `git tag -a v1.2.3 -m "Release version 1.2.3"`
6. Push tags: `git push origin --tags && git push upstream --tags`

## 📋 **Quality Checklist**

Before committing, ensure:

- [ ] Code follows PEP 8 standards
- [ ] All functions have type hints
- [ ] Docstrings are complete and accurate
- [ ] Tests pass (if applicable)
- [ ] Commit message follows conventional format
- [ ] Documentation is updated (if needed)
- [ ] English language used throughout
- [ ] Ready to push to both repositories

## 🛠️ **Tools & Scripts**

### Available Scripts
- `push-both-remotes.sh` - Push to origin and upstream
- `prepare-deployment-package.sh` - Create deployment package
- `smart-watchdog-sysv.sh` - Universal watchdog script

### Recommended Tools
- **Black** - Python code formatting
- **Flake8** - Python linting
- **MyPy** - Python type checking
- **Pre-commit** - Git hooks for quality checks

## 📞 **Support**

For questions about development standards:
1. Check this documentation first
2. Review existing code examples
3. Follow established patterns in the codebase
4. Maintain consistency with existing style

---

**Remember**: Consistency and clarity are key to maintainable code. Always prioritize readability and follow established conventions. 