# YouTubeTimestampRedditBot
Reddit bot that comments on posts that link to youtube and reference time, but don't include a timestamp in the link.

To run the main script
```bash
client_secret='$your_secret_here' client_id='$yor_id_here' poetry run python src/bot.py
```

Environment variables
```
log_level ["INFO", "WARNING", "NOTSET"]
client_id
client_secret
password
```

# Tests
```bash
poetry run task tests
```
