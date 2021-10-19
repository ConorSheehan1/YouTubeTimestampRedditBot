# Standard Library
import json
import logging
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
from src.utils.time_parsing import (
    TimestampParseError,
    convert_timestamp_to_seconds,
    get_title_time,
)
from src.utils.youtube import (
    add_timestamp_to_youtube_url,
    is_youtube_url_without_timestamp,
)

__version__ = "2.2.0"
LOGLEVEL = os.environ.get("log_level", "INFO").upper()
logger = setup_and_get_logger("bot.py", LOGLEVEL)


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

    def delete_bad_comments(self):
        for comment in self.r.user.me().comments.new(limit=25):
            reason_to_delete = self.should_delete_comment(comment)
            if reason_to_delete:
                logger.info(reason_to_delete)
                # json.dumps gives dict -> str formatting better than pprint
                comment_details = json.dumps(self.comment_to_dict(comment), indent=4)
                # pm bot self with comment details before deleting
                self.r.redditor(self.username).message(
                    reason_to_delete, comment_details
                )
                comment.delete()

    def should_delete_comment(self, comment) -> str:
        if comment.score < 1:
            return f"Deleting comment with low score {comment.score}"
        if any(["bad bot" in reply.body.lower() for reply in comment.replies]):
            return "Deleting comment with 'bad bot' reply"
        return ""

    def already_commented(self, submission) -> bool:
        return any(
            [comment.author.name == self.username for comment in submission.comments]
        )

    def submission_to_dict(self, submission, extra_info: dict = {}) -> dict:
        return {
            "reddit_permalink": f"{self.r.config.reddit_url}{submission.permalink}",
            "title": submission.title,
            "url": submission.url,
        }

    def comment_to_dict(self, comment) -> dict:
        return {
            "body": comment.body,
            "score": comment.score,
            "replies": [child.body for child in comment.replies],
            "thread": self.submission_to_dict(comment.submission),
        }

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
        yt_metadata = YouTube(submission.url)
        if convert_timestamp_to_seconds(raw_timestamp) >= yt_metadata.length:
            return False, "timestamp at or beyond yt bounds"
        if raw_timestamp in yt_metadata.title:
            return False, "timestamp in youtube title"
        if self.already_commented(submission):
            return False, "already commented"
        new_url = add_timestamp_to_youtube_url(submission.url, timestamp)
        comment = self.generate_comment(new_url)
        submission.reply(comment)
        return True, f"!!got one!! comment: {comment}"

    def stream_all_subreddits(self):
        self.login()
        for submission in self.r.subreddit("all").stream.submissions():
            print("-", end="", flush=True)
            commented, msg = self.handle_submission(submission)
            if msg:
                if getattr(logging, LOGLEVEL) <= logging.DEBUG:
                    submission_dict = self.submission_to_dict(submission)
                    submission_dict.update({"msg": msg})
                    logger.debug(submission_dict)
                else:
                    print(".", end="", flush=True)
            if commented:
                logger.info(
                    f"comment successful! sleeping for {self.comment_wait_time} minute(s)"
                )
                time.sleep(self.comment_wait_time * 60)
            self.delete_bad_comments()

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

    def test_specific(self, reddit_post_url: str):
        self.login()
        submission = self.r.submission(url=reddit_post_url)
        self.handle_submission(submission)


if __name__ == "__main__":
    load_dotenv()
    # need to cast to int for values coming from .env file
    CONNECTION_RETRY_LIMIT = int(os.getenv("connection_retry_limit", 3))
    CONNECTION_RETRY_WAIT_TIME = int(os.getenv("connection_retry_wait_time", 1))
    # can hit api limits if < 10
    COMMENT_WAIT_TIME = int(os.getenv("comment_wait_time", 10))
    GIT_REPO = os.getenv("git_repo", "")
    Bot(
        CONNECTION_RETRY_LIMIT, CONNECTION_RETRY_WAIT_TIME, COMMENT_WAIT_TIME, GIT_REPO
    ).main()
