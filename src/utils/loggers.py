# Standard Library
import logging
import os
from typing import Any, Callable, Generator, Tuple

# Third party
from praw.models import Comment, Submission
from rich.logging import RichHandler


def setup_and_get_logger(name: str, loglevel: str):
    logger = logging.getLogger(name)
    logging.basicConfig(level=loglevel, handlers=[RichHandler()])
    return logger


def generate_submission_rich_repr(reddit_url: str) -> Callable:
    def submission_rich_repr(self):
        yield "id", self.id
        yield "permalink", f"{reddit_url}{self.permalink}"
        yield "title", self.title
        yield "url", self.url

    return submission_rich_repr


def comment_rich_repr(self) -> Generator[Tuple[str, Any], None, None]:
    yield "id", self.id
    yield "body", self.body
    yield "score", self.score
    yield "replies", [child.body for child in self.replies]
    yield "submission", self.submission


def rich_to_str(self) -> str:
    """
    convert from rich_repr to markdown bulletlist like str
    """

    def format_pair(pair: Tuple, just=16, indent=4) -> str:
        indented_bullet = " " * indent + "*"
        if pair[0] == "submission":
            return f"{('* ' + pair[0] + ':')}\n{str(pair[1]).replace('*', indented_bullet)}"
        return f"{('* ' + pair[0] + ':').ljust(just)} {pair[1]}"

    return "\n".join([format_pair(tup) for tup in self.__rich_repr__()])


def monkey_patch_praw_objs(reddit_url: str):
    """
    monkeypatch praw models for better logging
    """
    Submission.__rich_repr__ = generate_submission_rich_repr(reddit_url)
    Submission.__str__ = rich_to_str
    Comment.__rich_repr__ = comment_rich_repr
    Comment.__str__ = rich_to_str
