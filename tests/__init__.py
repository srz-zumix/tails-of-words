try:
    import unittest2 as unittest
except:
    import unittest

def test_suite():
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('./tests')
    return test_suite
