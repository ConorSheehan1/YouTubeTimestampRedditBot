# Standard Library
import logging
import os
from typing import Any, Callable, Generator, Tuple

# Third party
from rich.logging import RichHandler


def setup_and_get_logger(name: str, loglevel: str):
    logger = logging.getLogger(name)
    logging.basicConfig(level=loglevel, handlers=[RichHandler()])
    return logger


def generate_submission_rich_repr(reddit_url: str) -> Callable:
    def submission_rich_repr(self):
        yield "id", self.id
        yield "reddit_permalink", f"{reddit_url}{self.permalink}"
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
            return f"{('* ' + pair[0] + ':').ljust(just + indent)}\n{str(pair[1]).replace('*', indented_bullet)}"
        return f"{('* ' + pair[0] + ':').ljust(just)} {pair[1]}"

    return "\n".join([format_pair(tup) for tup in self.__rich_repr__()])


# from rich.console import Console
# from rich.table import Table
# table = Table(width=50, overflow='fold')
# table.add_column()
# table.add_column()
# table.add_row("body", comment.body)
# table.add_row("score", str(comment.score))
# console = Console(record=True)
# console.print(table)
# s = console.export_text()
