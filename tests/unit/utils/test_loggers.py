# Standard Library
import unittest
from unittest.mock import patch

# YouTubeTimestampRedditBot
from src.utils.loggers import (
    comment_rich_repr,
    generate_submission_rich_repr,
    monkey_patch_praw_objs,
    rich_to_str,
)
from tests.mocks import MockComment, MockSubmission


class TestLoggers(unittest.TestCase):
    # def test_monkey_patch_praw_objs(self):
    #     import pdb; pdb.set_trace()
    #     monkey_patch_praw_objs('test_url')
    #     print('')

    # @patch('praw.models.Submission', MockSubmission)
    # @patch('praw.models.Comment', MockComment)
    # def test_rich_to_str(self):
    #     submission = MockSubmission(title="test", url="test")
    #     comment = MockComment(body="test body", score=1, replies=[])
    #     comment.submission = submission
    #     monkey_patch_praw_objs(reddit_url='test')
    #     expected = """* body: asdf
    #     """
    #     assert str(comment) == expected

    def test_rich_to_str(self):
        # basically same as monkeypatch_praw_objs
        MockSubmission.__rich_repr__ = generate_submission_rich_repr(
            reddit_url="reddit_test/"
        )
        MockSubmission.__str__ = rich_to_str
        MockComment.__rich_repr__ = comment_rich_repr
        MockComment.__str__ = rich_to_str

        submission = MockSubmission(title="test", url="test")
        comment = MockComment(body="test body", score=1, replies=[])
        comment.submission = submission
        expected = f"""* id:            test_comment
* body:          test body
* score:         1
* replies:       []
* submission:{'       '}
    * id:            test_submission
    * reddit_permalink: reddit_test/test_permalink
    * title:         test
    * url:           test"""
        assert str(comment) == expected
