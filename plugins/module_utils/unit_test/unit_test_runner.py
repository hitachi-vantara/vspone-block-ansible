import os
import unittest

# command to run this file: python unit_test_runner.py


def run_tests():
    current_directory = os.path.dirname(os.path.abspath(__file__))
    test_directory = os.path.join(current_directory)
    loader = unittest.TestLoader()
    suite = loader.discover(test_directory)
    runner = unittest.TextTestRunner()
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    if success:
        print("All tests passed!")
    else:
        print("Some tests failed.")
