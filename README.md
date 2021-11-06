[![Build Status](https://github.com/ConorSheehan1/YouTubeTimestampRedditBot/workflows/ci/badge.svg)](https://github.com/ConorSheehan1/YouTubeTimestampRedditBot/actions/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Tested python versions](https://img.shields.io/badge/dynamic/yaml?url=https://raw.githubusercontent.com/ConorSheehan1/YouTubeTimestampRedditBot/main/.github/workflows/ci.yml&label=Tested%20python%20versions&query=$.jobs.build.strategy.matrix.python)](https://github.com/ConorSheehan1/YouTubeTimestampRedditBot/blob/main/.github/workflows/ci.yml#L25)
[![YouTubeTimestampBot](https://img.shields.io/endpoint?url=https://botranks.com/api/getbadge/YouTubeTimestampBot&label=YouTubeTimestampBot%20rank)](https://botranks.com/?bot=YouTubeTimestampBot)

# YouTubeTimestampRedditBot
Sourecode for [u/YouTubeTimestampBot](https://www.reddit.com/user/YouTubeTimestampBot)

`YouTubeTimestampRedditBot` is a bot that searches [Reddit](https://www.reddit.com/) for posts which: 
1. link to [YouTube](https://www.youtube.com/)
2. reference a timestamp in the title
3. don't embed the timestamp in the link

It comments on those posts with an updated link that has the timestamp embedded, hopefully saving people precious milliseconds navigating to the time in the video.
