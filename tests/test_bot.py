# Standard Library
import unittest

# YouTubeTimestampRedditBot
from src.bot import Bot


class TestBot(unittest.TestCase):
    def test_generate_comment(self):
        expected = f"""Link that starts at the time OP mentioned: http://youtu.be/foo?t-1m2s
******************************************{'  '}
I'm a bot. Bleep bloop.{'  '}
[source](https://github.com/ConorSheehan1/YouTubeTimestampRedditBot) | version 1.1.0
"""
        actual = Bot().generate_comment("http://youtu.be/foo?t-1m2s")
        assert expected == actual
