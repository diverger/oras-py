#!/usr/bin/env python3

"""
Functional test to verify authentication fixes work correctly.
This test directly uses the functions where we added load_configs() calls.
"""

import os
import sys
from unittest.mock import Mock, patch

# Add the oras module to path so we can import it directly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import oras.provider
import oras.container


def test_delete_tag_calls_auth_loading():
    """Test that delete_tag function calls auth.load_configs()."""
    print("🔍 Testing delete_tag auth loading...")

    # Create registry with mocked auth
    registry = oras.provider.Registry(hostname="test.registry", insecure=True)
    container = oras.container.Container("test.registry/repo:tag")

    # Mock the auth and request methods
    registry.auth = Mock()
    registry.auth.load_configs = Mock()

    # Mock successful responses for delete_tag flow
    mock_head_response = Mock()
    mock_head_response.status_code = 200
    mock_head_response.headers = {"Docker-Content-Digest": "sha256:abc123"}

    mock_delete_response = Mock()
    mock_delete_response.status_code = 202

    with patch.object(registry, 'do_request', side_effect=[mock_head_response, mock_delete_response]):
        result = registry.delete_tag(container, "v1.0")

        # Verify auth.load_configs was called with the container
        registry.auth.load_configs.assert_called_once_with(container)
        assert result is True
        print("✅ delete_tag correctly calls auth.load_configs")

    return True


def test_get_tags_calls_auth_loading():
    """Test that get_tags function calls auth.load_configs()."""
    print("🔍 Testing get_tags auth loading...")

    registry = oras.provider.Registry(hostname="test.registry", insecure=True)
    container = oras.container.Container("test.registry/repo:tag")

    # Mock the auth and request methods
    registry.auth = Mock()
    registry.auth.load_configs = Mock()

    # Mock response for get_tags
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"tags": ["v1.0", "v2.0", "latest"]}
    mock_response.links = {}  # No pagination

    with patch.object(registry, 'do_request', return_value=mock_response):
        tags = registry.get_tags(container, N=10)

        # Verify auth.load_configs was called with the container
        registry.auth.load_configs.assert_called_once_with(container)
        assert isinstance(tags, list)
        assert "v1.0" in tags
        print("✅ get_tags correctly calls auth.load_configs")

    return True


def test_get_blob_calls_auth_loading():
    """Test that get_blob function calls auth.load_configs()."""
    print("🔍 Testing get_blob auth loading...")

    registry = oras.provider.Registry(hostname="test.registry", insecure=True)
    container = oras.container.Container("test.registry/repo:tag")

    # Mock the auth and request methods
    registry.auth = Mock()
    registry.auth.load_configs = Mock()

    # Mock response for get_blob
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.content = b"blob content"

    with patch.object(registry, 'do_request', return_value=mock_response):
        result = registry.get_blob(container, "sha256:abc123def456")

        # Verify auth.load_configs was called with the container
        registry.auth.load_configs.assert_called_once_with(container)
        assert result == mock_response
        print("✅ get_blob correctly calls auth.load_configs")

    return True


def test_blob_exists_calls_auth_loading():
    """Test that blob_exists function calls auth.load_configs()."""
    print("🔍 Testing blob_exists auth loading...")

    registry = oras.provider.Registry(hostname="test.registry", insecure=True)
    container = oras.container.Container("test.registry/repo:tag")

    # Mock the auth and request methods
    registry.auth = Mock()
    registry.auth.load_configs = Mock()

    # Mock response for blob_exists (HEAD request)
    mock_response = Mock()
    mock_response.status_code = 200

    layer = {"digest": "sha256:abc123def456", "size": 1024}

    with patch.object(registry, 'do_request', return_value=mock_response):
        result = registry.blob_exists(layer, container)

        # Verify auth.load_configs was called with the container
        registry.auth.load_configs.assert_called_once_with(container)
        assert result is True
        print("✅ blob_exists correctly calls auth.load_configs")

    return True


def test_auth_loading_with_string_container():
    """Test that auth loading works when container is passed as string."""
    print("🔍 Testing auth loading with string container...")

    registry = oras.provider.Registry(hostname="test.registry", insecure=True)

    # Mock the auth and request methods
    registry.auth = Mock()
    registry.auth.load_configs = Mock()

    # Mock response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"tags": ["latest"]}
    mock_response.links = {}

    with patch.object(registry, 'do_request', return_value=mock_response):
        # Call with string instead of Container object
        tags = registry.get_tags("test.registry/repo:latest", N=5)

        # Verify auth.load_configs was called
        registry.auth.load_configs.assert_called_once()

        # Get the actual container object that was passed
        called_container = registry.auth.load_configs.call_args[0][0]
        assert isinstance(called_container, oras.container.Container)
        print("✅ auth loading works with string container")

    return True


def test_auth_loading_early_in_functions():
    """Test that auth loading happens early in functions (before requests)."""
    print("🔍 Testing auth loading happens early...")

    registry = oras.provider.Registry(hostname="test.registry", insecure=True)
    container = oras.container.Container("test.registry/repo:tag")

    # Track call order
    call_order = []

    def mock_load_configs(*args):
        call_order.append("load_configs")

    def mock_do_request(*args, **kwargs):
        call_order.append("do_request")
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"tags": ["latest"]}
        mock_response.links = {}
        return mock_response

    registry.auth = Mock()
    registry.auth.load_configs = mock_load_configs

    with patch.object(registry, 'do_request', side_effect=mock_do_request):
        registry.get_tags(container)

        # Verify load_configs was called before do_request
        assert call_order[0] == "load_configs", f"Expected load_configs first, got {call_order}"
        assert "do_request" in call_order
        print("✅ auth loading happens before requests")

    return True


def main():
    """Run all functionality tests."""
    print("🚀 Testing authentication functionality fixes...")

    tests = [
        test_delete_tag_calls_auth_loading,
        test_get_tags_calls_auth_loading,
        test_get_blob_calls_auth_loading,
        test_blob_exists_calls_auth_loading,
        test_auth_loading_with_string_container,
        test_auth_loading_early_in_functions
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
                print(f"❌ Test {test.__name__} failed")
        except Exception as e:
            failed += 1
            print(f"❌ Test {test.__name__} crashed: {e}")

    print(f"\n📊 Results: {passed}/{len(tests)} tests passed")

    if failed == 0:
        print("🎉 All authentication functionality tests passed!")
        print("✅ Functions properly call auth.load_configs()")
        print("✅ Authentication loading happens at the right time")
        print("✅ Both Container objects and strings work correctly")
        return 0
    else:
        print("💥 Some tests failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
