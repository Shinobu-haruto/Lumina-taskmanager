import os
import pytest

@pytest.mark.linux
def test_linux_specific_functionality():
    # Example test for a functionality working in Linux
    assert os.name == 'posix'  # This checks if the OS is Linux

@pytest.mark.skipif(os.name != 'posix', reason="This test is for Linux only.")
def test_linux_only_feature():
    # Test for a feature that only exists in Linux
    assert True  # Replace with actual test logic

@pytest.mark.linux
def test_environment_variable():
    # Checking for an environment variable specific to Linux
    assert os.getenv('SOME_LINUX_VAR') is not None
