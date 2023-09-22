import unittest
from remove_html_markup import remove_html_markup


class RemoveHTMLMarkupTests(unittest.TestCase):

    def test_abc(self):
        self.assertEqual('abc', remove_html_markup(s='abc'))

    def test_b_abc_b(self):
        self.assertEqual('abc', remove_html_markup(s='<b>abc</b>'))

    def test_quoted_abc(self):
        self.assertEqual('"abc"', remove_html_markup(s='"abc"'))
