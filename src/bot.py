import os

import praw

reddit = praw.Reddit(
    client_id=os.getenv("client_id"),
    client_secret=os.getenv("client_secret"),
    user_agent="<console:YouTubeTimestampBot:0.1.0>",
)

for submission in reddit.subreddit("learnpython").hot(limit=10):
    print(submission.title, submission.url)
