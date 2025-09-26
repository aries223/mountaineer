# File: src/tests/run_tests.py

import unittest
import sys
import os

# Add the src directory to Python path so imports work correctly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def discover_and_run_tests():
    """Discover and run all test files in the tests directory"""
    # Discover all test modules (files starting with test_)
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests', pattern='test_*.py')

    # Run the discovered tests
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)

    return len(result.errors) + len(result.failures)

if __name__ == '__main__':
    print("Running automated tests...")
    error_count = discover_and_run_tests()

    if error_count > 0:
        sys.exit(1)  # Indicate test failures
    else:
        print("All tests passed!")
        sys.exit(0)
