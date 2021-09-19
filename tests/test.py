import sys

from tails_of_words.__main__ import CLI
from tails_of_words.__words__ import Words

try:
    import unittest2 as unittest
except:
    import unittest

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


class test_base(unittest.TestCase):

    def setUp(self):
        self.capture = StringIO()
        sys.stdout = self.capture
        return super(test_base, self).setUp()

    def tearDown(self):
        sys.stdout = sys.__stdout__
        self.capture.close()
        return super(test_base, self).tearDown()

    def stdoout(self):
        value = self.capture.getvalue()
        return value

class test_cli(test_base):

    def setUp(self):
        return super(test_cli, self).setUp()

    def tearDown(self):
        return super(test_cli, self).tearDown()

    def cli_run(self, opt):
        try:
            cli = CLI()
            cli.execute_with_args(opt)
        except SystemExit as e:
            output = self.stdoout()
            eprint(output)
            self.assertEqual(e.code, 0)

    def test_version(self):
        opt = ['--dumpversion']
        self.cli_run(opt)

    def test_show(self):
        sys.stdin = StringIO("テストだよ")
        opt = ['show', '-']
        self.cli_run(opt)
        output = self.stdoout()
        # eprint(output)
        self.assertNotEqual(output.find("名詞"), -1)

class test_words(test_base):

    def setUp(self):
        return super(test_words, self).setUp()

    def tearDown(self):
        return super(test_words, self).tearDown()

    def test_simple(self):
        words = Words()
        words.parse_string("テストだよ")
        self.assertEqual(1, len(words.lines))

    def test_strip(self):
        words = Words()
        words.parse_string(" テスト@だよ ")
        self.assertEqual(1, len(words.lines))
        self.assertEqual("テスト@だよ", words.lines[0].midasi)


if __name__ == '__main__':
    test_loader = unittest.defaultTestLoader
    test_runner = unittest.TextTestRunner()
    test_suite = test_loader.discover('.')
    test_runner.run(test_suite)
