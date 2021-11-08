# Standard Library
import unittest

# YouTubeTimestampRedditBot
from src.bot import Bot
from tests.mocks import MockSubmission, MockSubreddit


class TestBotIntegration(unittest.TestCase):
    def test_parse_submission_timestamp_in_yt_title(self):
        # https://www.reddit.com/r/gamingvids/comments/pwpt4k/resident_evil_3_mercenaries_mikhail_a_rank_2103/
        submission = MockSubmission(
            title="Resident Evil 3 Mercenaries - Mikhail A Rank 21:03",
            url="https://www.youtube.com/watch?v=bG4gZ8hXS0M",
        )
        assert Bot().parse_submission(submission) == (
            False,
            "timestamp in youtube title",
        )

    def test_parse_submission_timestamp_out_of_bounds(self):
        # length is 24:37
        submission = MockSubmission(
            title="Resident Evil 3 Mercenaries - Mikhail A Rank 24:37",
            url="https://www.youtube.com/watch?v=bG4gZ8hXS0M",
        )
        assert Bot().parse_submission(submission) == (
            False,
            "timestamp at or beyond yt bounds",
        )
