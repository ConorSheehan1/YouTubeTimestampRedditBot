# Standard Library
from typing import Generator, List, Union

# Third party
# required for inifinte width lookback (?<=\s|^)
# https://stackoverflow.com/a/40617321/6305204
import regex

# YouTubeTimestampRedditBot
from src.data.time_zones import time_zone_codes, time_zone_first_words

# note: lowercase for case insensitive match
excluded_prefixes = ["under", "less than", "sub", "in", "live", "live at", "live in"]
# don't need variations of live for suffixes
excluded_suffixes = ["am", "pm", "midday", "live"]
excluded_suffixes.extend(time_zone_codes)
excluded_suffixes.extend(time_zone_first_words)


class TimestampParseError(Exception):
    pass


def convert_numeric_time_to_yt(timestamp: str) -> str:
    """
    e.g. arg: 01:22:35
    returns:  01h22m35s
    """
    # cast to int and back for leading 0s
    time_components = [str(int(c)) for c in timestamp.split(":")]
    if len(time_components) > 3:
        raise TimestampParseError(f"Unparsable timestamp '{timestamp}'")
    yt_format_tuples = list(zip(time_components[::-1], ["s", "m", "h"]))
    yt_format_strings = ["".join(v) for v in yt_format_tuples]
    return "".join(yt_format_strings[::-1])


def has_excluded_prefix(title: str, numeric_timestamp: regex.Match) -> bool:
    # handle cases like `beaten under 3:00`
    # https://www.reddit.com/r/bindingofisaac/comments/ptfbgm/beating_greedier_mode_in_under_300_with_only_1/
    pre_timestamp = title[: numeric_timestamp.span()[0]]
    return any(
        [pre_timestamp.strip().lower().endswith(prefix) for prefix in excluded_prefixes]
    )


def has_excluded_suffix(title: str, numeric_timestamp: regex.Match) -> bool:
    # handle cases like `rally at 3:00 EST`
    # https://www.reddit.com/r/pga2k21/comments/pu2abg/will_be_reviewing_and_rating_a_hard_and_hardest/
    post_timestamp = title[numeric_timestamp.span()[1] :]
    return any(
        [
            post_timestamp.strip().lower().startswith(suffix)
            for suffix in excluded_suffixes
        ]
    )


def get_title_time(title: str) -> Union[str, bool]:
    # https://stackoverflow.com/questions/6713310/regex-specify-space-or-start-of-string-and-space-or-end-of-string
    # TODO: handle `Starting at like 3:14, this guy`
    space_or_start = r"(?<=\s|^)"
    hh_mm_ss = r"(((?:[0-9]?[0-9]:)?)([0-1]?[0-9]|2[0-3]):[0-5][0-9])"
    space_punctuation_or_end = r"(?=\s|\.\s|\,\s|$)"
    hh_mm_ss_regex = f"{space_or_start}{hh_mm_ss}{space_punctuation_or_end}"
    numeric_timestamp = regex.search(hh_mm_ss_regex, title)
    if numeric_timestamp:
        if has_excluded_prefix(title, numeric_timestamp):
            return False
        if has_excluded_suffix(title, numeric_timestamp):
            return False
        raw_matched_timestamp = numeric_timestamp.group()
        parsed_timestamp = convert_numeric_time_to_yt(raw_matched_timestamp)
        return parsed_timestamp
    return False
