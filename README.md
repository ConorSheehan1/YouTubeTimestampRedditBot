[![Build Status](https://github.com/ConorSheehan1/YouTubeTimestampRedditBot/workflows/ci/badge.svg)](https://github.com/ConorSheehan1/YouTubeTimestampRedditBot/actions/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Tested python versions](https://img.shields.io/badge/dynamic/yaml?url=https://raw.githubusercontent.com/ConorSheehan1/YouTubeTimestampRedditBot/main/.github/workflows/ci.yml&label=Tested%20python%20versions&query=$.jobs.build.strategy.matrix.python)](https://github.com/ConorSheehan1/YouTubeTimestampRedditBot/blob/main/.github/workflows/ci.yml#L25)

# YouTubeTimestampRedditBot
YouTubeTimestampRedditBot is a bot that searches reddit for posts which link to youtube and reference a timestamp, but don't include the timestamp in the link. It comments on those posts with an updated link including the timestamp, hopfully saving people precious milliseconds navigating to the time in the video.

### Installing dependencies
```bash
pip install poetry # only if needed
poetry install
```

To run the main script
```bash
poetry run python -m src/bot
# will need to run `poetry run task obtain_refresh_token`
# note: running src/bot.py directly will not work, since there a sibling modules which rely on each other
# (src.utils imports src.data)
# you can add environment variables to the .env file, or pass them directly. e.g.
refresh_token="token" client_secret='$secret' client_id='$id' poetry run python -m src/bot
```

Environment variables
```bash
# required
refresh_token
client_id
client_secret
# optional
password # prefer refresh_token instead
log_level ["INFO", "WARNING", "NOTSET"]
connection_retry_limit
# times are in minutes
connection_retry_wait_time
comment_wait_time # can hit api limits if < 10
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

### Development notes
See [dev.md](./dev.md)
