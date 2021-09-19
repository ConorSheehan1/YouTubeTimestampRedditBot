# Standard Library
import os
import re

# Third party
import praw

# YouTubeTimestampRedditBot
from utils.loggers import setup_and_get_logger
from utils.time_parsing import (
    TimestampParseError,
    get_title_time,
    generate_time_phrases,
)
from utils.youtube import is_youtube_url_without_timestamp, add_timestamp_to_youtube_url

__version__ = "0.1.0"
time_units = ["second", "minute"]
logger = setup_and_get_logger("bot.py")


class Bot:
    def __init__(self, time_units, time_limit: int = 60):
        self.time_units = time_units
        self.time_phrases = list(generate_time_phrases(time_units, time_limit))

    def login(self):
        self.r = praw.Reddit(
            client_id=os.getenv("client_id"),
            client_secret=os.getenv("client_secret"),
            user_agent=f"<console:YouTubeTimestampBot:{__version__}>",
        )

    def comment(self, new_url: str) -> str:
        # TODO: better way of keeping 2 spaces for markdown formatting?
        return f"""
Link that starts at the time OP mentioned: {new_url}
***********************{'  '}
I'm a bot. Bleep bloop.{'  '}
You can add a timestamp to any YouTub link using the `t` parameter. e.g.{'  '}
`youtube.com/some_video?t=1h2m34s`
"""

    def main(self):
        self.login()
        visited = 0  # doesn't work with stream
        # for submission in self.r.subreddit('all').hot(limit=1000):
        for submission in self.r.subreddit("all").stream.submissions():
            logger.info(
                {"visited": visited, "title": submission.title, "url": submission.url}
            )
            if is_youtube_url_without_timestamp(submission.url):
                try:
                    timestamp = get_title_time(submission.title)
                except TimestampParseError:
                    logger.error(
                        f"Failed to parse title {submission.title}. Error:\n{e}"
                    )
                    continue  # go to next submission

                if timestamp:
                    new_url = add_timestamp_to_youtube_url(submission.url, timestamp)
                    # https://www.reddit.com/r/redditdev/comments/ajme22/praw_get_the_posts_actual_url/eewp6ee?utm_source=share&utm_medium=web2x&context=3
                    logger.info(
                        f"""found one!
reddit_url: {self.r.config.reddit_url}{submission.permalink}
title: {submission.title}
url: {submission.url}
"""
                    )
                    print(self.comment(new_url))

    def test_specific(self):
        submission = self.r.submission(
            url="https://www.reddit.com/r/cringe/comments/pfliwd/starting_at_like_314_this_guy_attempts_some_of/"
        )
        # print(submission.title, submission.url, self.is_youtube_url_without_timestamp(submission.url), self.get_title_time(submission.title))
        if is_youtube_url_without_timestamp(submission.url):
            try:
                timestamp = self.get_title_time(submission.title)
            except TimestampParseError:
                logger.error(f"Failed to parse title {submission.title}")

            if timestamp:
                new_url = add_timestamp_to_youtube_url(submission.url, timestamp)
                print(self.comment(new_url))


if __name__ == "__main__":
    Bot(time_units).main()
