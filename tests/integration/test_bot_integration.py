# Standard Library
import unittest

# YouTubeTimestampRedditBot
from src.bot import Bot


class MockSubreddit:
    def __init__(self, display_name: str, user_is_banned: bool):
        self.display_name = display_name
        self.user_is_banned = user_is_banned


class MockSubmission:
    def __init__(
        self,
        title: str,
        url: str,
        display_name: str = "foo",
        user_is_banned: bool = False,
    ):
        self.title = title
        self.url = url
        self.subreddit = MockSubreddit(display_name, user_is_banned)

    def reply(*args):
        return args


class TestBotIntegration(unittest.TestCase):
    def test_handle_submission_timestamp_in_yt_title(self):
        # https://www.reddit.com/r/gamingvids/comments/pwpt4k/resident_evil_3_mercenaries_mikhail_a_rank_2103/
        submission = MockSubmission(
            title="Resident Evil 3 Mercenaries - Mikhail A Rank 21:03",
            url="https://www.youtube.com/watch?v=bG4gZ8hXS0M",
        )
        assert Bot().handle_submission(submission) == (
            False,
            "timestamp in youtube title",
        )
