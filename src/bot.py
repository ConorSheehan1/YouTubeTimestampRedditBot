import os
import re
from typing import Generator, List

import inflect
import praw

__version__ = "0.1.0"
time_units = ["second", "minute"]
p = inflect.engine()


def generate_time_phrases(
    units: List[str], limit: int = 59
) -> Generator[str, None, None]:
    """
    returns: strings like 'one second', 'two seconds' etc.
    """
    for unit in units:
        yield f"one {unit}"
        for i in range(2, limit):
            yield f"{p.number_to_words(i)} {p.plural(unit)}"


class Bot:
    def __init__(self, time_units, time_limit: int = 59):
        self.time_units = time_units
        self.time_phrases = list(generate_time_phrases(time_units, time_limit))

    def is_youtube_url_without_timestamp(self, url: str) -> bool:
        # is the url a youtube url https://regexr.com/3dj5t
        yt_regex = r"((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube\.com|youtu.be))"
        if not re.match(yt_regex, url):
            return False
        # if ?t= or &t= is in the url, it already has a timestamp
        if any(t in url for t in ["?t=", "&t="]):
            return False
        return True

    def title_has_time(self, title: str) -> bool:
        # basic time reference MM:SS e.g. 1:23
        # TODO: fix false positive 24:23 matches on 4:23, which is valid, but 24:anything is not valid
        # TODO: allow HH:MM:SS?
        # TODO: return parsed time stamp instead of True, e.g. "Crazy stuff at 30 seconds in" -> "0m30s"
        basic_time_regex = r"([0-1]?[0-9]|2[0-3]):[0-5][0-9]"
        if re.match(basic_time_regex, title):
            return True
        # only need to check for singular version, since it's always a substring.
        # e.g. 'thirty seconds' and 'one second' both contain 'second'.
        if any([unit in title for unit in self.time_units]):
            if any([time_phrase in title for time_phrase in self.time_phrases]):
                return True
        return False

    def main(self):
        reddit = praw.Reddit(
            client_id=os.getenv("client_id"),
            client_secret=os.getenv("client_secret"),
            user_agent=f"<console:YouTubeTimestampBot:{__version__}>",
        )

        for submission in reddit.subreddit("cringe").new(limit=10):
            print(
                submission.title,
                submission.url,
                self.is_youtube_url_without_timestamp(submission.url),
                self.title_has_time(submission.title),
            )


if __name__ == "__main__":
    Bot(time_units).main()
