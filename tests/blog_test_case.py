import unittest

class BlogTestCase(unittest.TestCase):

    def read_html_file(self, blog_name):
        with open("tests/" + blog_name + ".html", "r") as f:
            content = f.read()
        return content

    def assert_starts_with(self, text, content):
        self.assertTrue(content.startswith(text.decode("utf-8")))

    def assert_text_in_content(self, text, content):
        self.assertTrue(text.decode("utf-8") in content)

    def assert_ends_with(self, text, content):
        self.assertTrue(content.endswith(text.decode("utf-8")))
