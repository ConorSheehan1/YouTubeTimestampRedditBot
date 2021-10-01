# Standard Library
import os
import time
from typing import Tuple

# Third party
import praw
from dotenv import load_dotenv
from prawcore.exceptions import RequestException, ResponseException, ServerError
from pytube import YouTube
from requests.exceptions import ConnectionError, ReadTimeout

# YouTubeTimestampRedditBot
from src.data.subreddits import blacklist
from src.utils.loggers import setup_and_get_logger
from src.utils.time_parsing import TimestampParseError, get_title_time
from src.utils.youtube import (
    add_timestamp_to_youtube_url,
    is_youtube_url_without_timestamp,
)

__version__ = "1.2.0"
logger = setup_and_get_logger("bot.py")


class Bot:
    def __init__(
        self,
        connection_retry_limit: int = 3,
        connection_retry_wait_time: int = 1,
        comment_wait_time: int = 10,
        git_repo: str = "",
    ):
        self.blacklist = blacklist
        self.username = "YouTubeTimestampBot"
        self.version = __version__
        self.connection_retry_limit = connection_retry_limit
        self.connection_retry_wait_time = connection_retry_wait_time
        self.comment_wait_time = comment_wait_time
        self.git_repo = git_repo

    def login(self):
        login_kwargs = {
            "user_agent": f"<console:{self.username}:{self.version}>",
            "username": self.username,
            "client_id": os.getenv("client_id"),
            "client_secret": os.getenv("client_secret"),
        }
        # https://www.reddit.com/r/GoldTesting/comments/3cm1p8/how_to_make_your_bot_use_oauth2/
        refresh_token = os.getenv("refresh_token")
        if refresh_token:
            login_kwargs["refresh_token"] = refresh_token
        else:
            login_kwargs["password"] = os.getenv("password")
        self.r = praw.Reddit(**login_kwargs)

    def generate_footer(self) -> str:
        base = f"version {self.version}"
        if self.git_repo:
            return f"[source]({self.git_repo}) | {base}"
        return base

    def generate_comment(self, new_url: str) -> str:
        return f"""Link that starts at the time OP mentioned: {new_url}
******************************************{'  '}
I'm a bot. Bleep bloop.{'  '}
{self.generate_footer()}
"""

    def already_commented(self, submission):
        return any(
            [comment.author.name == self.username for comment in submission.comments]
        )

    def log_submission(self, submission, extra_info={}):
        default_info = {
            "reddit_permalink": f"{self.r.config.reddit_url}{submission.permalink}",
            "title": submission.title,
            "url": submission.url,
        }
        default_info.update(extra_info)
        logger.info(default_info)

    def handle_submission(self, submission) -> Tuple[bool, str]:
        if submission.subreddit.display_name.lower() in self.blacklist:
            return False, "subreddit in blacklist"
        if submission.subreddit.user_is_banned:
            return False, "user is banned"
        if not is_youtube_url_without_timestamp(submission.url):
            return False, ""
        try:
            reddit_title_timestamp = get_title_time(submission.title)
        except TimestampParseError as e:
            logger.error(
                f"Failed to parse reddit title {submission.title}. Error:\n{e}"
            )
            return False, ""
        if not reddit_title_timestamp:
            return False, "no timestamp in reddit title"
        timestamp, raw_timestamp = reddit_title_timestamp
        yt_metadata = YouTube(submission.url).streams.first()
        if raw_timestamp in yt_metadata.title:
            return False, "timestamp in youtube title"
        if self.already_commented(submission):
            return False, "already commented"
        new_url = add_timestamp_to_youtube_url(submission.url, timestamp)
        comment = self.generate_comment(new_url)
        # https://www.reddit.com/r/redditdev/comments/ajme22/praw_get_the_posts_actual_url/eewp6ee?utm_source=share&utm_medium=web2x&context=3
        submission.reply(comment)
        return True, f"!!got one!! comment: {comment}"

    def stream_all_subreddits(self):
        self.login()
        for submission in self.r.subreddit("all").stream.submissions():
            commented, msg = self.handle_submission(submission)
            if msg:
                log_submission(submission, {"msg": msg})
            if commented:
                logger.info(
                    f"comment successful! sleeping for {self.comment_wait_time} minute(s)"
                )
                time.sleep(self.comment_wait_time * 60)

    def main(self):
        retries = 0
        while retries < self.connection_retry_limit:
            try:
                self.stream_all_subreddits()
            except (
                RequestException,
                ResponseException,
                ServerError,
                ConnectionError,
                ReadTimeout,
            ) as e:
                retries += 1
                logger.error(f"Error:\n{e}")
                logger.info(f"Retrying in {self.connection_retry_wait_time} minute(s).")
                time.sleep(self.connection_retry_wait_time * 60)

    def test_specific(self, reddit_post_url):
        self.login()
        submission = self.r.submission(url=reddit_post_url)
        self.handle_submission(submission)


if __name__ == "__main__":
    load_dotenv()
    # need to cast to int for values coming from .env file
    CONNECTION_RETRY_LIMIT = int(os.getenv("connection_retry_limit", 3))
    CONNECTION_RETRY_WAIT_TIME = int(os.getenv("connection_retry_wait_time", 1))
    COMMENT_WAIT_TIME = int(
        os.getenv("comment_wait_time", 10)
    )  # can hit api limits if < 10
    GIT_REPO = os.getenv("git_repo", "")
    Bot(
        CONNECTION_RETRY_LIMIT, CONNECTION_RETRY_WAIT_TIME, COMMENT_WAIT_TIME, GIT_REPO
    ).main()
