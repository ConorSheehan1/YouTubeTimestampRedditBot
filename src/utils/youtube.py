# Standard Library
import re

# Third party
from furl import furl


def is_youtube_url_without_timestamp(url: str) -> bool:
    # is the url a youtube url https://regexr.com/3dj5t
    yt_regex = r"((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube\.com|youtu.be))"
    if not re.search(yt_regex, url):
        return False
    # if ?t= or &t= is in the url, it already has a timestamp
    if any(t in url for t in ["?t=", "&t="]):
        return False
    return True


def add_timestamp_to_youtube_url(url: str, timestamp: str) -> str:
    # https://stackoverflow.com/a/24791840/6305204
    return furl(url).add({"t": timestamp}).url
