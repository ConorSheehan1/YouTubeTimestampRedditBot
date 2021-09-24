[![Build Status](https://github.com/ConorSheehan1/YouTubeTimestampRedditBot/workflows/ci/badge.svg)](https://github.com/ConorSheehan1/YouTubeTimestampRedditBot/actions/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# YouTubeTimestampRedditBot
YouTubeTimestampRedditBot is a bot that searches reddit for posts which link to youtube and reference a timestamp, but don't include the timestamp in the link. It comments on those posts with an updated link including the timestamp, hopfully saving people precious milliseconds navigating to the time in the video.

To run the main script
```bash
client_secret='$your_secret_here' client_id='$yor_id_here' poetry run python -m src/bot
# note: running src/bot.py directly will not work, since there a sibling modules which rely on each other
# (src.utils imports src.data)
```

Environment variables
```
log_level ["INFO", "WARNING", "NOTSET"]
client_id
client_secret
refresh_token
password # prefer refersh_token instead
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
