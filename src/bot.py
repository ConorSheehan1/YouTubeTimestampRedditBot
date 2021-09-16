import os

import praw

__version__ = "0.1.0"
reddit = praw.Reddit(
    client_id=os.getenv("client_id"),
    client_secret=os.getenv("client_secret"),
    user_agent=f"<console:YouTubeTimestampBot:{__version__}>",
)

for submission in reddit.subreddit("learnpython").hot(limit=10):
    print(submission.title, submission.url)
