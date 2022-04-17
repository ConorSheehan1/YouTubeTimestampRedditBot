# Standard Library
import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

# Third party
from freezegun import freeze_time

# YouTubeTimestampRedditBot
from src.bot import Bot
from tests.mocks import MockComment


class TestBot(unittest.TestCase):
    def test_generate_comment_with_git_repo(self):
        expected = f"""Link that starts at the time OP mentioned: http://youtu.be/foo?t-1m2s{'  '}
******************************************{'  '}
I'm a bot, bleep bloop.{'  '}
[source](test) | [issues](test/issues) | version 2.4.6
"""
        actual = Bot(git_repo="test").generate_comment("http://youtu.be/foo?t-1m2s")
        assert expected == actual

    def test_generate_comment_without_git_repo(self):
        expected = f"""Link that starts at the time OP mentioned: http://youtu.be/foo?t-1m2s{'  '}
******************************************{'  '}
I'm a bot, bleep bloop.{'  '}
version 2.4.6
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

    @patch("time.sleep")
    def test_handle_comment_sleep(self, patched_time_sleep):
        """
        bot commented at 12:00 and found another post to comment on at 12:01.
        should sleep for 9 minutes.
        """
        bot = Bot(comment_wait_time=10)
        with freeze_time("2020-01-01 12:00"):
            bot.last_commented = datetime.now()
        with freeze_time("2020-01-01 12:01"):
            bot.handle_comment_sleep()
        # sleep for 9 minutes
        patched_time_sleep.assert_called_with(9 * 60)

    @patch("time.sleep")
    def test_handle_comment_no_sleep(self, patched_time_sleep):
        """
        bot should not sleep if the last comment was longer ago than comment_wait_time
        """
        bot = Bot(comment_wait_time=10)
        with freeze_time("2020-01-01 12:00"):
            bot.last_commented = datetime.now()
        with freeze_time("2020-01-01 12:10"):
            bot.handle_comment_sleep()
        # should not sleep at all since last comment was 10 minutes ago
        assert not patched_time_sleep.called

    def test_handle_delete_bad_comments(self):
        """
        bot should check for bad comments if last checked > 10 minutes ago
        """
        bot = Bot()
        bot.delete_bad_comments = MagicMock()
        with freeze_time("2020-01-01 12:00"):
            bot.last_checked_bad_comments = datetime.now()
        with freeze_time("2020-01-01 12:10"):
            bot.handle_delete_bad_comments()
        assert bot.delete_bad_comments.called

    def test_handle_delete_bad_comments_not_run(self):
        """
        bot should not check for bad comments if last checked < 10 minutes ago
        """
        bot = Bot(check_bad_comment_wait_time=10)
        bot.delete_bad_comments = MagicMock()
        with freeze_time("2020-01-01 12:00"):
            bot.last_checked_bad_comments = datetime.now()
        with freeze_time("2020-01-01 12:09"):
            bot.handle_delete_bad_comments()
        assert not bot.delete_bad_comments.called
