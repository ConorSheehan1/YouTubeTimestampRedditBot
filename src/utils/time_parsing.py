# Standard Library
from typing import Generator, List, Union

# Third party
import inflect

# required for inifinte width lookback (?<=\s|^)
# https://stackoverflow.com/a/40617321/6305204
import regex

p = inflect.engine()
excluded_prefixes = ["under", "less than", "in"]
# expected prefixes ["at", "around"]
# handle passing words e.g. ["like"]


class TimestampParseError(Exception):
    pass


def generate_time_phrases(
    units: List[str], limit: int = 60
) -> Generator[str, None, None]:
    """
    returns: strings like 'one second', 'two seconds' etc.
    """
    for unit in units:
        yield f"one {unit}"
        for i in range(2, limit):
            yield f"{p.number_to_words(i)} {p.plural(unit)}"


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


def get_title_time(title: str) -> Union[str, bool]:
    # https://stackoverflow.com/questions/6713310/regex-specify-space-or-start-of-string-and-space-or-end-of-string
    space_or_start = r"(?<=\s|^)"
    hh_mm_ss = r"(((?:[0-9]?[0-9]:)?)([0-1]?[0-9]|2[0-3]):[0-5][0-9])"
    space_or_end = r"(?=\s|$)"
    hh_mm_ss_regex = f"{space_or_start}{hh_mm_ss}{space_or_end}"
    numeric_timestamp = regex.search(hh_mm_ss_regex, title)
    if numeric_timestamp:
        # handle cases like `beaten under 3:00`
        # https://www.reddit.com/r/bindingofisaac/comments/ptfbgm/beating_greedier_mode_in_under_300_with_only_1/
        pre_timestamp = title[: numeric_timestamp.span()[0]]
        if any(
            [
                pre_timestamp.strip().lower().endswith(prefix)
                for prefix in excluded_prefixes
            ]
        ):
            return False

        raw_matched_timestamp = numeric_timestamp.group()
        parsed_timestamp = convert_numeric_time_to_yt(raw_matched_timestamp)

        # TODO: include logging without breaking tests
        # logger.info({"title": title, "raw_matched_timestamp": raw_matched_timestamp, "parsed_timestamp": parsed_timestamp})
        return parsed_timestamp
    # # only need to check for singular version, since it's always a substring.
    # # e.g. 'thirty seconds' and 'one second' both contain 'second'.
    # if any([unit in title for unit in self.time_units]):
    #     for time_phrase in self.time_phrase:
    #         if time_phrase in title:
    #             return time_phrase
    return False
