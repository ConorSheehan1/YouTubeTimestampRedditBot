# Standard Library
import json
import logging
import os
import time
from datetime import datetime
from typing import Tuple

# Third party
import praw
from dotenv import load_dotenv
from praw.models import Comment, Submission
from prawcore.exceptions import RequestException, ResponseException, ServerError
from pytube import YouTube
from requests.exceptions import ConnectionError, ReadTimeout

# YouTubeTimestampRedditBot
from src.data.subreddits import blacklist, min_karma_dict
from src.utils.loggers import monkey_patch_praw_objs, setup_and_get_logger
from src.utils.time_parsing import (
    TimestampParseError,
    convert_timestamp_to_seconds,
    get_title_time,
)
from src.utils.youtube import (
    add_timestamp_to_youtube_url,
    is_youtube_url_without_timestamp,
)

__version__ = "2.4.7"
LOGLEVEL = os.environ.get("log_level", "INFO").upper()
logger = setup_and_get_logger("bot.py", LOGLEVEL)


class Bot:
    def __init__(
        self,
        connection_retry_limit: int = 3,
        connection_retry_wait_time: int = 1,
        comment_wait_time: int = 10,
        check_bad_comment_wait_time: int = 10,
        batch_submission_limit: int = 1000,
        git_repo: str = "",
    ):
        self.blacklist = blacklist
        self.min_karma_dict = min_karma_dict
        self.username = "YouTubeTimestampBot"
        self.version = __version__
        self.connection_retry_limit = connection_retry_limit
        self.connection_retry_wait_time = connection_retry_wait_time
        self.comment_wait_time = comment_wait_time
        self.check_bad_comment_wait_time = check_bad_comment_wait_time
        self.batch_submission_limit = batch_submission_limit
        self.git_repo = git_repo
        self.last_commented = datetime.now()
        self.last_checked_bad_comments = datetime.now()
        self.stream_log = ""

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
        monkey_patch_praw_objs(self.r.config.reddit_url)

    def generate_footer(self) -> str:
        version = f"version {self.version}"
        if self.git_repo:
            return f"[source]({self.git_repo}) | [issues]({self.git_repo}/issues) | {version}"
        return version

    def generate_comment(self, new_url: str) -> str:
        return f"""Link that starts at the time OP mentioned: {new_url}{'  '}
******************************************{'  '}
I'm a bot, bleep bloop.{'  '}
{self.generate_footer()}
"""

    def delete_bad_comments(self):
        for comment in self.r.user.me().comments.new(limit=25):
            reason_to_delete = self.should_delete_comment(comment)
            if reason_to_delete:
                logger.info(reason_to_delete)
                # pm bot self with comment details before deleting
                self.r.redditor(self.username).message(reason_to_delete, str(comment))
                comment.delete()

    def should_delete_comment(self, comment: Comment) -> str:
        if comment.score < 1:
            return f"Deleting comment with low score {comment.score}"
        if any(["bad bot" in reply.body.lower() for reply in comment.replies]):
            return "Deleting comment with 'bad bot' reply"
        return ""

    def already_commented(self, submission: Submission) -> bool:
        return any(
            [comment.author.name == self.username for comment in submission.comments]
        )

    def parse_submission(self, submission: Submission) -> Tuple[bool, str]:
        """check if submission meets bot criteria, and if it does, comment on the submission."""
        subreddit_name = submission.subreddit.display_name.lower()
        min_karma_requirement = self.min_karma_dict.get(subreddit_name, 0)
        comment_karma = self.r.redditor(self.username).comment_karma
        if subreddit_name in self.blacklist:
            return False, "subreddit in blacklist"
        if submission.subreddit.user_is_banned:
            return False, "user is banned"
        # assume bot only ever gets comment karma, since it doesn't create posts
        if min_karma_requirement > comment_karma:
            return (
                False,
                f"need {min_karma_requirement} karma to post in {subreddit_name}, only have {comment_karma}",
            )
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
        # add 3 second buffer for human error when putting video length in title
        if (title_time := convert_timestamp_to_seconds(raw_timestamp)) >= (
            yt_time := yt_metadata.length - 3
        ):
            return False, f"timestamp {title_time} at or beyond yt bounds {yt_time}"
        if raw_timestamp in yt_metadata.title:
            return False, "timestamp in youtube title"
        if self.already_commented(submission):
            return False, "already commented"
        new_url = add_timestamp_to_youtube_url(submission.url, timestamp)
        comment = self.generate_comment(new_url)
        submission.reply(comment)
        return True, f"!!got one!! comment: {comment}"

    def handle_comment_sleep(self):
        """
        determine how long bot should sleep for after commenting.
        e.g. comment_wait_time = 10 (minutes)
        last_commented 1 minute ago
        sleep for 9 minutes before commenting again
        """
        now = datetime.now()
        delta = now - self.last_commented
        self.last_commented = now
        max_seconds_to_sleep = self.comment_wait_time * 60
        if delta.seconds < max_seconds_to_sleep:
            min_seconds_to_sleep = max_seconds_to_sleep - delta.seconds
            logger.info(
                f"comment successful! sleeping for {min_seconds_to_sleep} second(s)"
            )
            time.sleep(min_seconds_to_sleep)

    def handle_delete_bad_comments(self):
        """
        determine if bot should check for bad comments.
        only check every 10 minutes to avoid rate limits.
        """
        check_bad_comments_seconds = self.check_bad_comment_wait_time * 60
        now = datetime.now()
        delta = now - self.last_checked_bad_comments
        if delta.seconds >= check_bad_comments_seconds:
            logger.info("checking for bad comments")
            self.delete_bad_comments()
            self.last_checked_bad_comments = datetime.now()

    def append_to_stream_log(self, v: str):
        # short output to avoid flooding logs but show bot is still running and parsing posts
        self.stream_log += v
        if len(self.stream_log) > 50:
            logger.info(self.stream_log)
            self.stream_log = ""

    def handle_submission(self, submission: Submission):
        self.append_to_stream_log("-")
        commented, msg = self.parse_submission(submission)
        if msg:
            if getattr(logging, LOGLEVEL) <= logging.DEBUG:
                submission_dict = dict(submission.__rich_repr__())
                submission_dict.update({"msg": msg})
                logger.debug(submission_dict)
            else:
                self.append_to_stream_log(".")
        if commented:
            self.handle_comment_sleep()
        self.handle_delete_bad_comments()

    def stream_new_submissions(self):
        """continuosly stream new submissions to all subreddits"""
        self.login()
        for submission in self.r.subreddit("all").stream.submissions():
            self.handle_submission(submission)

    def batch_rising_submissions(self):
        """parse a set number of rising submissions. use with cron"""
        self.login()
        for submission in self.r.subreddit("all").rising(
            limit=self.batch_submission_limit
        ):
            self.handle_submission(submission)

    def parse_specific_submission(self, reddit_post_url: str):
        self.login()
        submission = self.r.submission(url=reddit_post_url)
        self.parse_submission(submission)

    def main(self):
        retries = 0
        while retries < self.connection_retry_limit:
            try:
                self.stream_new_submissions()
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


if __name__ == "__main__":
    load_dotenv()
    # need to cast to int for values coming from .env file
    CONNECTION_RETRY_LIMIT = int(os.getenv("connection_retry_limit", 3))
    CONNECTION_RETRY_WAIT_TIME = int(os.getenv("connection_retry_wait_time", 1))
    # can hit api limits if < 10
    COMMENT_WAIT_TIME = int(os.getenv("comment_wait_time", 10))
    CHECK_BAD_COMMENT_WAIT_TIME = int(os.getenv("check_bad_comment_wait_time", 10))
    BATCH_SUBMISSION_LIMIT = int(os.getenv("batch_submission_limit", 1000))
    GIT_REPO = os.getenv("git_repo", "")
    Bot(
        connection_retry_limit=CONNECTION_RETRY_LIMIT,
        connection_retry_wait_time=CONNECTION_RETRY_WAIT_TIME,
        comment_wait_time=COMMENT_WAIT_TIME,
        check_bad_comment_wait_time=CHECK_BAD_COMMENT_WAIT_TIME,
        batch_submission_limit=BATCH_SUBMISSION_LIMIT,
        git_repo=GIT_REPO,
    ).main()
