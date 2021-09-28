# Standard Library
import unittest

# YouTubeTimestampRedditBot
from src.bot import Bot


class TestBot(unittest.TestCase):
    def test_generate_comment_with_git_repo(self):
        expected = f"""Link that starts at the time OP mentioned: http://youtu.be/foo?t-1m2s
******************************************{'  '}
I'm a bot. Bleep bloop.{'  '}
[source](test) | version 1.2.0
"""
        actual = Bot(git_repo="test").generate_comment("http://youtu.be/foo?t-1m2s")
        assert expected == actual

    def test_generate_comment_without_git_repo(self):
        expected = f"""Link that starts at the time OP mentioned: http://youtu.be/foo?t-1m2s
******************************************{'  '}
I'm a bot. Bleep bloop.{'  '}
version 1.2.0
"""
        actual = Bot().generate_comment("http://youtu.be/foo?t-1m2s")
        assert expected == actual
