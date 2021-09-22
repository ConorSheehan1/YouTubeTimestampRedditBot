# Standard Library
import os
import time

# Third party
import praw

# YouTubeTimestampRedditBot
from utils.loggers import setup_and_get_logger
from utils.time_parsing import (
    TimestampParseError,
    generate_time_phrases,
    get_title_time,
)
from utils.youtube import add_timestamp_to_youtube_url, is_youtube_url_without_timestamp

__version__ = "0.1.0"
time_units = ["second", "minute"]
logger = setup_and_get_logger("bot.py")


class Bot:
    def __init__(self, time_units, time_limit: int = 60):
        self.time_units = time_units
        self.time_phrases = list(generate_time_phrases(time_units, time_limit))
        # https://www.reddit.com/wiki/bottiquette omit /r/suicidewatch and /r/depression
        # note: lowercase for case insensitive match
        self.blacklist = ["suicidewatch", "depression", "hololive"]

    def login(self):
        self.r = praw.Reddit(
            client_id=os.getenv("client_id"),
            client_secret=os.getenv("client_secret"),
            user_agent=f"<console:YouTubeTimestampBot:{__version__}>",
            username="YouTubeTimestampBot",
            password=os.getenv("password")  # TODO: switch to oauth
            # https://www.reddit.com/r/GoldTesting/comments/3cm1p8/how_to_make_your_bot_use_oauth2/
        )

    def generate_comment(self, new_url: str) -> str:
        # TODO: better way of keeping 2 spaces for markdown formatting?
        return f"""
Link that starts at the time OP mentioned: {new_url}
***********************{'  '}
I'm a bot. Bleep bloop.
"""

    def handle_submission(self, submission):
        if not is_youtube_url_without_timestamp(submission.url):
            return False

        logger.info({"title": submission.title, "url": submission.url})
        try:
            timestamp = get_title_time(submission.title)
        except TimestampParseError:
            logger.error(f"Failed to parse title {submission.title}. Error:\n{e}")
            return False

        if not timestamp:
            return False

        new_url = add_timestamp_to_youtube_url(submission.url, timestamp)
        # import pdb; pdb.set_trace()
        comment = self.generate_comment(new_url)
        # https://www.reddit.com/r/redditdev/comments/ajme22/praw_get_the_posts_actual_url/eewp6ee?utm_source=share&utm_medium=web2x&context=3
        logger.info(
            {
                "msg": "!!!youtube link missing timestamp!!!",
                "reddit_url": f"{self.r.config.reddit_url}{submission.permalink}",
                "title": submission.title,
                "url": submission.url,
                "comment": comment,
            }
        )
        submission.reply(comment)
        return True

    def main(self):
        self.login()
        for submission in self.r.subreddit("all").stream.submissions():
            # TODO: switch to whitelist?
            if submission.subreddit.display_name.lower() in self.blacklist:
                continue

            commented = self.handle_submission(submission)
            if commented:
                logger.info("comment successful! sleeping for 11 minutes")
                # TODO: better way to avoid api limit, continue processing but don't comment unless last was at least 10 minutes ago
                # avoid api timeout for spamming comments
                time.sleep(11 * 60)  # sleep for 11 minutes after commenting

    # def test_specific(self):
    #     self.login()
    #     # submission = self.r.submission(
    #     #     url="https://www.reddit.com/r/cringe/comments/pfliwd/starting_at_like_314_this_guy_attempts_some_of/"
    #     # )
    #     # submission = self.r.submission(
    #     #     url="https://www.reddit.com/r/classicalmusic/comments/psr6s6/the_dude_at_232_same_bro"
    #     # )
    #     self.handle_submission(submission)


if __name__ == "__main__":
    Bot(time_units).main()
    # Bot(time_units).test_specific()
