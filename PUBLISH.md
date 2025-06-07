# Publishing Guide for FlagVault Python SDK

## Pre-publish Checklist

- [ ] All tests pass: `pytest`
- [ ] No linting errors: `flake8 flagvault_sdk tests`
- [ ] Code is formatted: `black flagvault_sdk tests`
- [ ] Version bumped in `flagvault_sdk/__init__.py`
- [ ] CHANGELOG.md updated with release notes
- [ ] README.md is up to date
- [ ] Examples work with new changes

## Publishing Steps

### 1. Clean Previous Builds

```bash
rm -rf dist/ build/ *.egg-info/
```

### 2. Build Package

```bash
python -m build
```

This creates both wheel and source distributions in `dist/`:
- `flagvault_sdk-1.0.0-py3-none-any.whl`
- `flagvault_sdk-1.0.0.tar.gz`

### 3. Test Package Locally

```bash
# Create a test virtual environment
python -m venv test_env
source test_env/bin/activate  # On Windows: test_env\Scripts\activate

# Install the built package
pip install dist/flagvault_sdk-1.0.0-py3-none-any.whl

# Test it works
python -c "from flagvault_sdk import FlagVaultSDK; print('Import successful')"

# Clean up
deactivate
rm -rf test_env
```

### 4. Upload to Test PyPI (Optional but Recommended)

```bash
# Install/upgrade twine
pip install --upgrade twine

# Upload to Test PyPI
python -m twine upload --repository testpypi dist/*

# Test installation from Test PyPI
pip install --index-url https://test.pypi.org/simple/ --no-deps flagvault-sdk
```

### 5. Upload to Production PyPI

```bash
# Upload to PyPI
python -m twine upload dist/*
```

You'll be prompted for your PyPI username and password (or token).

### 6. Verify Publication

1. Check PyPI page: https://pypi.org/project/flagvault-sdk/
2. Install from PyPI in a clean environment:
   ```bash
   pip install flagvault-sdk
   ```

### 7. Create GitHub Release

1. Tag the release:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

2. Create release on GitHub with:
   - Release notes from CHANGELOG.md
   - Link to PyPI package
   - Migration guide for breaking changes

## Authentication Setup

### Using API Token (Recommended)

1. Create API token at https://pypi.org/manage/account/token/
2. Create `~/.pypirc` file:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-AgEIcHlwaS5vcmcC...your-token-here

[testpypi]
username = __token__
password = pypi-AgEIcHlwaS5vcmcC...your-test-token-here
```

## Troubleshooting

### Version Already Exists

PyPI doesn't allow overwriting existing versions. Bump the version in `__init__.py`:

```python
__version__ = "1.0.1"  # Increment appropriately
```

### Missing Files in Package

Check `MANIFEST.in` to ensure all necessary files are included. Test with:

```bash
python -m build
tar -tzf dist/flagvault_sdk-1.0.0.tar.gz
```

### Build Errors

Ensure you have the latest build tools:

```bash
pip install --upgrade build twine
```

## Post-Publish

1. Update documentation site with new version
2. Announce release in Discord/Slack
3. Update example repositories
4. Monitor PyPI downloads and issues
5. Update any dependent projects