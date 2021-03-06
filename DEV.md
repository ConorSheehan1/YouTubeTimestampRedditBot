## Installing dependencies
```bash
pip install poetry
poetry install
```

## To run the main script
```bash
poetry run python -m src/bot
# note: running src/bot.py directly will not work, since there a sibling modules which rely on each other (src.utils imports src.data)
# you may also need to include PYTHONPATH=$(pwd)
# 1. if you don't have a refresh_token run `poetry run task obtain_refresh_token`
# 2. add environment variables to the .env file, or pass them directly. e.g.
PYTHONPATH=$(pwd) refresh_token="token" client_secret='$secret' client_id='$id' poetry run python -m src/bot
```

## Environment variables
```bash
# required
refresh_token
client_id
client_secret
# optional
password # prefer refresh_token instead
log_level ["NOTSET", "DEBUG", "INFO", "WARNING"] # https://docs.python.org/3/library/logging.html#levels
connection_retry_limit
# times are in minutes
connection_retry_wait_time
comment_wait_time # can hit api limits if < 10
check_bad_comment_wait_time
batch_submission_limit
git_repo # optionally include link to github in comment footer
```

### Tests
```bash
poetry run task tests
```

### Linting
```bash
poetry run task lint
poetry run task isort
poetry run task mypy
```

### GitHooks
To setup git hooks run:
```bash
poetry run pre-commit install
```

### Version management
```bash
# pass args e.g. patch, minor, major, choose to commit changes or not
poetry run bumpversion --commit --tag patch
# once the tag is built by the release action, check the attached .tar is installable.
# e.g. `pip install git+https://github.com/ConorSheehan1/shot@v0.1.1`
# if it is update the release draft and pre-release state.
```
### Detect secrets
```bash
# scan all files
git ls-files -z | xargs -0 poetry run detect-secrets-hook --baseline .secrets.baseline

# create new baseline
poetry run detect-secrets scan --baseline .secrets.baseline
```

# Reddit
To see app settings, go to https://www.reddit.com/prefs/apps  
Docs: https://praw.readthedocs.io/en/stable/getting_started/quick_start.html  
YT example: https://www.youtube.com/watch?v=3FpqXyJsd1s

## Refresh token
```bash
poetry run task obtain_refresh_token
```

# Heroku setup
https://github.com/moneymeets/python-poetry-buildpack
```bash
# if missing heroku git remote locally, append `--app youtube-timestamp-reddit-bot`
heroku login
heroku buildpacks:clear
heroku buildpacks:add https://github.com/moneymeets/python-poetry-buildpack.git
heroku buildpacks:add heroku/python

# can also set env vars in Heroku UI
# https://stackoverflow.com/questions/12680859/are-heroku-config-vars-safe-for-sensitive-information
heroku config:set PYTHON_RUNTIME_VERSION=3.9.7
heroku config:set client_id=$client_id
heroku config:set client_secret=$client_secret
heroku config:set refresh_token=$refresh_token
```

Note commits to main branch are automatically deployed using heroku pipeline.

## Heroku scheduler
would be useful to run batches in cron, but need to add creditcard to use heroku scheduler / any add-on.
revolute didn't work.

# Design
This bot has been designed to avoid external dependencies.
It currently relies on python, its packages, and a reddit account.
It does not rely on:
1. Databases
  Some bots use a database to keep track of submissions they've already seen.
  This bot checks if it has already commented on a thread.
2. Email services
  Some bots send emails before deleting own comments.
  This bot sends a pm to itself for later debugging.
  Note: now that the bot deletes its own comments, this may cause issues.
  If it does, or if changing from new to rising causes it to happen, a db may be required.
