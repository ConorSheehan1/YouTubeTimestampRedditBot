# Standard Library
import unittest

# YouTubeTimestampRedditBot
from src.bot import Bot
from tests.mocks import MockComment


class TestBot(unittest.TestCase):
    def test_generate_comment_with_git_repo(self):
        expected = f"""Link that starts at the time OP mentioned: http://youtu.be/foo?t-1m2s
******************************************{'  '}
I'm a bot. Bleep bloop.{'  '}
[source](test) | version 2.2.0
"""
        actual = Bot(git_repo="test").generate_comment("http://youtu.be/foo?t-1m2s")
        assert expected == actual

    def test_generate_comment_without_git_repo(self):
        expected = f"""Link that starts at the time OP mentioned: http://youtu.be/foo?t-1m2s
******************************************{'  '}
I'm a bot. Bleep bloop.{'  '}
version 2.2.0
"""
        actual = Bot().generate_comment("http://youtu.be/foo?t-1m2s")
        assert expected == actual

    def test_should_delete_comment(self):
        comments = [
            {
                "comment": MockComment("test body", 0, []),
                "expected_output": "Deleting comment with low score 0",
            },
            {
                "comment": MockComment("test body", 1, [MockComment("bad bot")]),
                "expected_output": "Deleting comment with 'bad bot' reply",
            },
            {"comment": MockComment("test body", 1, []), "expected_output": ""},
        ]
        for (i, d) in enumerate(comments):
            with self.subTest(i=i):
                actual = Bot().should_delete_comment(d["comment"])
                assert actual == d["expected_output"]
