#!/usr/bin/env python3

"""
Quick validation script to ensure our test setup is ready for GitHub.
"""

import os
import sys


def main():
    print("🔍 Validating test setup for GitHub workflow...")

    # Check that our test file exists
    test_file = "oras/tests/test_auth_functionality.py"
    if not os.path.exists(test_file):
        print(f"❌ Test file missing: {test_file}")
        return 1
    print(f"✅ Test file exists: {test_file}")

    # Check that workflow file exists
    workflow_file = ".github/workflows/test-auth-fixes.yml"
    if not os.path.exists(workflow_file):
        print(f"❌ Workflow file missing: {workflow_file}")
        return 1
    print(f"✅ Workflow file exists: {workflow_file}")

    # Check that provider.py has our auth fixes
    provider_file = "oras/provider.py"
    with open(provider_file, 'r') as f:
        content = f.read()

    auth_calls = content.count('self.auth.load_configs(container)')
    if auth_calls < 4:
        print(f"❌ Expected at least 4 auth.load_configs calls, found {auth_calls}")
        return 1
    print(f"✅ Found {auth_calls} auth.load_configs calls in provider.py")

    # Syntax check
    result = os.system(f"python -m py_compile {provider_file}")
    if result != 0:
        print("❌ provider.py has syntax errors")
        return 1
    print("✅ provider.py syntax is valid")

    # Test file syntax check
    result = os.system(f"python -m py_compile {test_file}")
    if result != 0:
        print("❌ test file has syntax errors")
        return 1
    print("✅ test file syntax is valid")

    print("\n🎉 All validation checks passed!")
    print("📤 Ready to push to GitHub and run the workflow!")

    return 0


if __name__ == "__main__":
    sys.exit(main())
