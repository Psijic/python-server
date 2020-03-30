import unittest

from server import *


# TBD
class MyTestCase(unittest.TestCase):
    def test_allowed_file(self):
        self.assertFalse(allowed_file("wrong_name"))
        self.assertTrue(allowed_file("right_name" + ALLOWED_EXTENSIONS[0]))
        self.assertTrue(allowed_file("right_name.mp3" + ALLOWED_EXTENSIONS[-1]))

    def test_file_exists(self):
        self.assertFalse(file_exists("fake_video.jp2000"))


if __name__ == '__main__':
    unittest.main()
