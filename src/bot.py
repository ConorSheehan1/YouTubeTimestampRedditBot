import logging
import os
import re
from typing import Generator, List

import inflect
import praw
from furl import furl

__version__ = "0.1.0"
time_units = ["second", "minute"]
p = inflect.engine()
logger = logging.getLogger("bot.py")
logging.basicConfig()
# log everything, not just warnings
logging.root.setLevel(logging.NOTSET)


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


class TimestampParseError(Exception):
    pass


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

    def convert_numeric_time_to_yt(self, timestamp: str) -> str:
        """
        e.g. arg: 01:22:35
        returns:  01h22m35s
        """
        time_components = timestamp.split(":")
        if len(time_components) > 3:
            raise TimestampParseError(f"Unparsable timestamp {timestamp}")
        yt_format_tuples = list(zip(time_components[::-1], ["s", "m", "h"]))
        yt_format_strings = ["".join(v) for v in yt_format_tuples]
        return "".join(yt_format_strings[::-1])

    def get_title_time(self, title: str) -> str:
        # basic time reference MM:SS e.g. 1:23
        # TODO: allow HH:MM:SS?
        # TODO: fix false positive 24:23 matches on 4:23, which is valid, but 24:anything is not valid
        basic_time_regex = r"(([0-1]?[0-9]|2[0-3]):[0-5][0-9])"
        numeric_timestamp = re.search(basic_time_regex, title)
        if numeric_timestamp:
            parsed_timestamp = self.convert_numeric_time_to_yt(
                numeric_timestamp.group()
            )
            logger.info(
                f"""title:\t\t\t{title}
    raw matched timestamp:\t{numeric_timestamp.group()}
    parsed timestamp:\t\t{parsed_timestamp}
    """
            )
            return parsed_timestamp
        # # only need to check for singular version, since it's always a substring.
        # # e.g. 'thirty seconds' and 'one second' both contain 'second'.
        # if any([unit in title for unit in self.time_units]):
        #     for time_phrase in self.time_phrase:
        #         if time_phrase in title:
        #             logger.info(f"""
        #             title: {title}
        #             raw matched timestamp: {time_phrase}
        #             parsed timestamp: {time_phrase}
        #             """) # TODO: parse time_phrases, e.g. https://github.com/akshaynagpal/w2n
        #             return time_phrase
        return False

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
        # for submission in reddit.subreddit("cringe").new(limit=10):
        #     print(
        #         submission.title,
        #         submission.url,
        #         self.is_youtube_url_without_timestamp(submission.url),
        #         self.get_title_time(submission.title),
        #     )

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
