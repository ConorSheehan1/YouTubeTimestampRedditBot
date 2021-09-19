# Standard Library
import os
import re
from typing import Generator, List

# Third party
import inflect
import praw
from furl import furl

# YouTubeTimestampRedditBot
from logging_utils import setup_and_get_logger
from time_utils import TimestampParseError, get_title_time

__version__ = "0.1.0"
time_units = ["second", "minute"]
p = inflect.engine()
logger = setup_and_get_logger("bot.py")


def generate_time_phrases(
    units: List[str], limit: int = 60
) -> Generator[str, None, None]:
    """
    returns: strings like 'one second', 'two seconds' etc.
    """
    for unit in units:
        yield f"one {unit}"
        for i in range(2, limit):
            yield f"{p.number_to_words(i)} {p.plural(unit)}"


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

    def is_youtube_url_without_timestamp(self, url: str) -> bool:
        # is the url a youtube url https://regexr.com/3dj5t
        yt_regex = r"((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube\.com|youtu.be))"
        if not re.search(yt_regex, url):
            return False
        # if ?t= or &t= is in the url, it already has a timestamp
        if any(t in url for t in ["?t=", "&t="]):
            return False
        return True

    def add_timestamp_to_youtube_url(self, url: str, timestamp: str) -> str:
        # https://stackoverflow.com/a/24791840/6305204
        return furl(url).add({"t": timestamp}).url

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
            if self.is_youtube_url_without_timestamp(submission.url):
                try:
                    timestamp = get_title_time(submission.title)
                except TimestampParseError:
                    logger.error(
                        f"Failed to parse title {submission.title}. Error:\n{e}"
                    )
                    continue  # go to next submission

                if timestamp:
                    # Standard Library
                    import pdb

                    pdb.set_trace()
                    new_url = self.add_timestamp_to_youtube_url(
                        submission.url, timestamp
                    )
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
        if self.is_youtube_url_without_timestamp(submission.url):
            try:
                timestamp = self.get_title_time(submission.title)
            except TimestampParseError:
                logger.error(f"Failed to parse title {submission.title}")

            if timestamp:
                new_url = self.add_timestamp_to_youtube_url(submission.url, timestamp)
                print(self.comment(new_url))


if __name__ == "__main__":
    Bot(time_units).main()
