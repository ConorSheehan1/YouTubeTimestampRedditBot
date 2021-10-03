# Standard Library
import unittest

# YouTubeTimestampRedditBot
from src.utils.time_parsing import (
    TimestampParseError,
    convert_numeric_time_to_yt,
    convert_yt_to_seconds,
    get_title_time,
)


class TestTimeParsing(unittest.TestCase):
    def test_convert_numeric_time_to_yt(self):
        dicts = [
            {"input": "01:22:35", "expected_output": "1h22m35s"},
            {"input": "12:34", "expected_output": "12m34s"},
            {"input": "12", "expected_output": "12s"},
            {"input": "0012", "expected_output": "12s"},
            {"input": "00:12", "expected_output": "0m12s"},
        ]

        for (i, d) in enumerate(dicts):
            with self.subTest(i=i):
                assert convert_numeric_time_to_yt(d["input"]) == d["expected_output"]

    def test_convert_numeric_time_to_yt_error(self):
        timestamp = "1:2:3:4"
        with self.assertRaises(TimestampParseError) as context:
            # only allow up to hh:mm:ss, anything above is probably not valid time for yt
            convert_numeric_time_to_yt(timestamp)

        # GOTCHA: test will pass regardless of this assertion, if indented within assertRaises context manager
        self.assertIn(f"Unparsable timestamp '{timestamp}'", str(context.exception))

    def test_convert_yt_to_seconds(self):
        dicts = [
            {"input": "01:22:35", "expected_output": 4955},
            {"input": "12:34", "expected_output": 754},
            {"input": "12", "expected_output": 12},
            {"input": "0012", "expected_output": 12},
            {"input": "00:12", "expected_output": 12},
            {"input": "01:10", "expected_output": 70},
        ]

        for (i, d) in enumerate(dicts):
            with self.subTest(i=i):
                assert convert_yt_to_seconds(d["input"]) == d["expected_output"]

    def test_convert_yt_to_seconds_error(self):
        timestamp = "1:2:3:4"
        with self.assertRaises(TimestampParseError) as context:
            # only allow up to hh:mm:ss, anything above is probably not valid time for yt
            convert_yt_to_seconds(timestamp)

        # GOTCHA: test will pass regardless of this assertion, if indented within assertRaises context manager
        self.assertIn(f"Unparsable timestamp '{timestamp}'", str(context.exception))

    def test_get_title_time(self):
        dicts = [
            {
                "input": "Starts at 01:22:35",
                "expected_output": ("1h22m35s", "01:22:35"),
            },
            {"input": "Cool thing at 12:34", "expected_output": ("12m34s", "12:34")},
            {"input": "23:34 cool thing", "expected_output": ("23m34s", "23:34")},
            {
                "input": "The dude at 2:32. Same bro!",
                "expected_output": ("2m32s", "2:32"),
            },
            {
                "input": "Starting at like 3:14, this guy says dumb stuff.",
                "expected_output": ("3m14s", "3:14"),
            },
            {"input": "The dude at 2:32.Not a timestamp", "expected_output": False},
            {
                "input": "Starting at like 3:14,12 not a timestamp",
                "expected_output": False,
            },
            {"input": "bad time 00:61", "expected_output": False},
            {"input": "bad time 60:51", "expected_output": False},
            {"input": "bad time 25:50:51", "expected_output": False},
            {"input": "days not supported yet 2:21:50:51", "expected_output": False},
            {"input": "[23:34] cool thing", "expected_output": False},
            {"input": "23:34] cool thing", "expected_output": False},
            {"input": "[23:34 cool thing", "expected_output": False},
            {"input": "Cool thing at 60:34", "expected_output": False},
            {
                "input": "Cool thing around 24:34",
                "expected_output": ("24m34s", "24:34"),
            },
            {"input": "Cool thing around 24:64", "expected_output": False},
            {"input": "Not a time [34m]", "expected_output": False},
            {"input": "This has no numbers in it", "expected_output": False},
            {
                "input": "This has numbers that don't look like time 123.456",
                "expected_output": False,
            },
            {"input": "Around 12 seconds something happens", "expected_output": False},
            {
                "input": "Documentary at 01:12:34",
                "expected_output": ("1h12m34s", "01:12:34"),
            },
            {"input": "r/hololive (Sep 22 @ 21:00JST)", "expected_output": False},
            {
                "input": "Documentary [00:12:34]",
                "expected_output": False,
            },  # r/documentaries format
            # excluded prefixes
            {"input": "1:20 scale", "expected_output": False},
            {"input": "beaten in under 3:00", "expected_output": False},
            {"input": "finished in less than 3:00", "expected_output": False},
            {"input": "done in 3:00", "expected_output": False},
            {"input": "first sub 3:00 lap", "expected_output": False},
            {"input": "episode 2:01", "expected_output": False},
            {"input": "live 3:00", "expected_output": False},
            {"input": "live at 3:00", "expected_output": False},
            {"input": "live in 3:00", "expected_output": False},
            {"input": "broke 3:00 record", "expected_output": False},
            {"input": "broke the 3:00 barrier", "expected_output": False},
            # excluded suffixes
            {"input": "thing at 3:00 live", "expected_output": False},
            {"input": "thing at 3:00 pm", "expected_output": False},
            {"input": "thing at 3:00 PM", "expected_output": False},
            {"input": "thing at 3:00 am", "expected_output": False},
            {"input": "thing at 3:00 midday", "expected_output": False},
            {"input": "thing at 3:00 jst", "expected_output": False},
            {"input": "thing at 3:00 EST", "expected_output": False},
            # no space and also timezone
            {"input": "thing at 3:00PST", "expected_output": False},
            # time zone first word
            {"input": "thing at 3:00 Eastern", "expected_output": False},
        ]

        for (i, d) in enumerate(dicts):
            with self.subTest(i=i):
                assert get_title_time(d["input"]) == d["expected_output"]
