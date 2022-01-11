# Standard Library
from typing import List


class Struct:
    def __init__(self, **entries):
        self.__dict__.update(entries)


class MockSubreddit:
    def __init__(self, display_name: str, user_is_banned: bool):
        self.display_name = display_name
        self.user_is_banned = user_is_banned


class MockSubmission:
    def __init__(
        self,
        title: str,
        url: str,
        subreddit_display_name: str = "foo",
        user_is_banned: bool = False,
    ):
        self.id = "test_submission"
        self.title = title
        self.url = url
        self.subreddit = MockSubreddit(subreddit_display_name, user_is_banned)
        self.permalink = "test_permalink"

    def reply(*args):
        return args


class MockComment:
    def __init__(self, body: str, score: int = 0, replies: List = []):
        self.id = "test_comment"
        self.body = body
        self.score = score
        self.replies = replies

    def delete(self):
        return True
