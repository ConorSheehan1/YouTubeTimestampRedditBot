# Standard Library
import unittest

# YouTubeTimestampRedditBot
from src.bot import Bot
from tests.mocks import MockSubmission, MockSubreddit, Struct


def create_bot():
    b = Bot()
    b.r = Struct(**{"redditor": lambda x: Struct(**{"comment_karma": 1000})})
    return b


class TestBotIntegration(unittest.TestCase):
    def test_parse_submission_timestamp_in_yt_title(self):
        # https://www.reddit.com/r/gamingvids/comments/pwpt4k/resident_evil_3_mercenaries_mikhail_a_rank_2103/
        submission = MockSubmission(
            title="Resident Evil 3 Mercenaries - Mikhail A Rank 21:03",
            url="https://www.youtube.com/watch?v=bG4gZ8hXS0M",
        )
        assert create_bot().parse_submission(submission) == (
            False,
            "timestamp in youtube title",
        )

    def test_parse_submission_timestamp_out_of_bounds(self):
        # length is 24:37
        submission = MockSubmission(
            title="Resident Evil 3 Mercenaries - Mikhail A Rank 24:37",
            url="https://www.youtube.com/watch?v=bG4gZ8hXS0M",
        )
        assert create_bot().parse_submission(submission) == (
            False,
            "timestamp at or beyond yt bounds",
        )

    def test_min_karma_requirement(self):
        submission = MockSubmission(
            title="foo at 12:34",
            url="https://www.youtube.com/watch?v=bG4gZ8hXS0M",
            subreddit_display_name="Superstonk",
        )
        assert create_bot().parse_submission(submission) == (
            False,
            "need 1200 karma to post in superstonk, only have 1000",
        )
