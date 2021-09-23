# Installing dependencies
```bash
pip install poetry # only if needed
poetry install
```

# GitHooks
To setup git hooks run:
```bash
pre-commit install
```

# Reddit
To see app settings, go to https://www.reddit.com/prefs/apps
Docs: https://praw.readthedocs.io/en/stable/getting_started/quick_start.html
YT example: https://www.youtube.com/watch?v=3FpqXyJsd1s

# Heroku setup
https://github.com/moneymeets/python-poetry-buildpack
```bash
heroku login
heroku buildpacks:clear --app youtube-timestamp-reddit-bot
heroku buildpacks:add https://github.com/moneymeets/python-poetry-buildpack.git --app youtube-timestamp-reddit-bot
heroku buildpacks:add heroku/python --app youtube-timestamp-reddit-bot
```

Note commits to main branch are automatically deployed using heroku pipeline.
