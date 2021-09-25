# Standard Library
import unittest

# YouTubeTimestampRedditBot
from src.utils.time_parsing import (
    TimestampParseError,
    convert_numeric_time_to_yt,
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

    def test_get_title_time(self):
        dicts = [
            {"input": "Starts at 01:22:35", "expected_output": "1h22m35s"},
            {"input": "Cool thing at 12:34", "expected_output": "12m34s"},
            {"input": "23:34 cool thing", "expected_output": "23m34s"},
            {"input": "The dude at 2:32. Same bro!", "expected_output": "2m32s"},
            {
                "input": "Starting at like 3:14, this guy says dumb stuff.",
                "expected_output": "3m14s",
            },
            {"input": "The dude at 2:32.Not a timestamp", "expected_output": False},
            {
                "input": "Starting at like 3:14,12 not a timestamp",
                "expected_output": False,
            },
            {"input": "[23:34] cool thing", "expected_output": False},
            {"input": "23:34] cool thing", "expected_output": False},
            {"input": "[23:34 cool thing", "expected_output": False},
            {"input": "Cool thing at 60:34", "expected_output": False},
            {"input": "Cool thing around 24:34", "expected_output": False},
            {"input": "Not a time [34m]", "expected_output": False},
            {"input": "This has no numbers in it", "expected_output": False},
            {
                "input": "This has numbers that don't look like time 123.456",
                "expected_output": False,
            },
            {
                "input": "Around 12 seconds something happens",
                "expected_output": False,
            },  # will be handled with time phrases
            {"input": "Documentary at 01:12:34", "expected_output": "1h12m34s"},
            {"input": "r/hololive (Sep 22 @ 21:00JST)", "expected_output": False},
            {
                "input": "Documentary [00:12:34]",
                "expected_output": False,
            },  # r/documentaries format
            # excluded prefixes
            {"input": "beaten in under 3:00", "expected_output": False},
            {"input": "finished in less than 3:00", "expected_output": False},
            {"input": "done in 3:00", "expected_output": False},
            {"input": "live 3:00", "expected_output": False},
            {"input": "live at 3:00", "expected_output": False},
            {"input": "live in 3:00", "expected_output": False},
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
