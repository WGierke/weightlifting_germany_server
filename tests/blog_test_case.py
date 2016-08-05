import unittest

class BlogTestCase(unittest.TestCase):

    def read_html_file(self, blog_name):
        with open("tests/" + blog_name + ".html", "r") as f:
            content = f.read()
        return content

    def assert_text_in_content(self, text, content):
        self.assertTrue(text.decode("utf-8") in content)
