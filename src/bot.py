# Standard Library
import os
import time

# Third party
import praw
from dotenv import load_dotenv
from prawcore.exceptions import RequestException, ResponseException, ServerError
from requests.exceptions import ConnectionError, ReadTimeout

# YouTubeTimestampRedditBot
from src.data.subreddits import blacklist
from src.utils.loggers import setup_and_get_logger
from src.utils.time_parsing import TimestampParseError, get_title_time
from src.utils.youtube import (
    add_timestamp_to_youtube_url,
    is_youtube_url_without_timestamp,
)

__version__ = "1.0.1"
logger = setup_and_get_logger("bot.py")
load_dotenv()
# need to cast to int for values coming from .env file
CONNECTION_RETRY_LIMIT = int(os.getenv("connection_retry_limit", 3))
CONNECTION_RETRY_WAIT_TIME = int(os.getenv("connection_retry_wait_time", 1))
COMMENT_WAIT_TIME = int(
    os.getenv("comment_wait_time", 10)
)  # can hit api limits if < 10
GIT_REPO = os.getenv("git_repo")


class Bot:
    def __init__(self):
        self.blacklist = blacklist
        self.username = "YouTubeTimestampBot"
        self.version = __version__

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
        if GIT_REPO:
            return f"[source]({GIT_REPO}) | {base}"
        return base

    def generate_comment(self, new_url: str) -> str:
        # TODO: better way of keeping 2 spaces for markdown formatting?
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
            "reddit_url": f"{self.r.config.reddit_url}{submission.permalink}",
            "title": submission.title,
            "url": submission.url,
        }
        default_info.update(extra_info)
        logger.info(default_info)

    def handle_submission(self, submission):
        if not is_youtube_url_without_timestamp(submission.url):
            return False
        try:
            timestamp = get_title_time(submission.title)
        except TimestampParseError:
            logger.error(f"Failed to parse title {submission.title}. Error:\n{e}")
            return False
        if not timestamp:
            self.log_submission(submission, {"msg": "no timestamp found"})
            return False
        if self.already_commented(submission):
            self.log_submission(submission, {"msg": "already commented"})
            return False
        new_url = add_timestamp_to_youtube_url(submission.url, timestamp)
        comment = self.generate_comment(new_url)
        # https://www.reddit.com/r/redditdev/comments/ajme22/praw_get_the_posts_actual_url/eewp6ee?utm_source=share&utm_medium=web2x&context=3

        self.log_submission(submission, {"msg": "!!!got one!!!", "comment": comment})
        submission.reply(comment)
        return True

    def stream_all_subreddits(self):
        self.login()
        for submission in self.r.subreddit("all").stream.submissions():
            if submission.subreddit.display_name.lower() in self.blacklist:
                continue
            commented = self.handle_submission(submission)
            if commented:
                logger.info(
                    f"comment successful! sleeping for {COMMENT_WAIT_TIME} minutes"
                )
                time.sleep(COMMENT_WAIT_TIME * 60)

    def main(self):
        retries = 0
        while retries < CONNECTION_RETRY_LIMIT:
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
                logger.info(f"Retrying in {CONNECTION_RETRY_WAIT_TIME} minute.")
                time.sleep(CONNECTION_RETRY_WAIT_TIME * 60)

    def test_specific(self, reddit_post_url):
        self.login()
        submission = self.r.submission(url=reddit_post_url)
        self.handle_submission(submission)


if __name__ == "__main__":
    Bot().main()
