# Installing dependencies
```bash
pip install poetry # only if needed
poetry install
```

## GitHooks
To setup git hooks run:
```bash
poetry run pre-commit install
```

# Reddit
To see app settings, go to https://www.reddit.com/prefs/apps
Docs: https://praw.readthedocs.io/en/stable/getting_started/quick_start.html
YT example: https://www.youtube.com/watch?v=3FpqXyJsd1s

## Refresh token
```bash
poetry run task obtain_refresh_token
```

### Version management
```bash
# pass args e.g. patch, minor, major, choose to commit changes or not
poetry run bumpversion --commit --tag patch
# once the tag is built by the release action, check the attached .tar is installable.
# e.g. `pip install git+https://github.com/ConorSheehan1/shot@v0.1.1`
# if it is update the release draft and pre-release state.
```

# Heroku setup
https://github.com/moneymeets/python-poetry-buildpack
```bash
# if missing heroku git remote locally, append `--app youtube-timestamp-reddit-bot`
heroku login
heroku buildpacks:clear
heroku buildpacks:add https://github.com/moneymeets/python-poetry-buildpack.git
heroku buildpacks:add heroku/python

# https://stackoverflow.com/questions/12680859/are-heroku-config-vars-safe-for-sensitive-information
heroku config:set PYTHON_RUNTIME_VERSION=3.9.7
heroku config:set client_id=$client_id
heroku config:set client_secret=$client_secret
heroku config:set refresh_token=$refresh_token
```

Note commits to main branch are automatically deployed using heroku pipeline.
